import telebot.async_telebot as async_telebot
from telebot.types import Message, ReactionTypeEmoji
from ..types.databases.database import Database
from enum import Enum
from typing import Literal
import datetime
import os
import logging

class Event_Type(Enum):
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"
    DEBUG = "debug"

class States(Enum):
    ACTIVE = "active"
    EXPERIMENTAL = "experimental" # will use it later ig
    DISABLED = "disabled"
    TEMPLATE = "template"

class DsbModule:    
    def __init__(self, bot: async_telebot.AsyncTeleBot) -> None:
        self._state = States.DISABLED
        self._bot = bot
        self._commands = {}
    
    def set_state(self, state: Literal["active", "experimental", "disabled"]):
        self._state = States(state)
        if self._state == States.ACTIVE or self._state == States.EXPERIMENTAL:
            self._add_handlers()
        elif self._state == States.DISABLED:
            self._add_blank_handlers()

    def log_event(self, event: str, event_type: Literal["info", "warning", "debug", "error"]) -> None:
        os.makedirs("logs", exist_ok=True)
        
        with open(f"logs/log{datetime.datetime.today().date()}.txt", "a") as log:
            type = event_type.upper() if isinstance(event_type, str) else event_type.value.upper()
            log.write(f"[{type}]: {event}\n")

    def _add_handlers(self) -> None:
        for command in self._commands:
            self._bot.register_message_handler(self._commands[command], commands=[command], pass_bot=True)
    
    def _add_blank_handlers(self) -> None:
        for command in self._commands:
            self._bot.register_message_handler(self._maintenance_break, commands=[command], pass_bot=True)
    
    async def _blank_response(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        await bot.reply_to(message, "This function is not implemented yet")
    
    async def _maintenance_break(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        await bot.reply_to(message, "This function is currently not avaible")

    async def _confirm(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ will react to the message with a thumbs up emoji to confirm the action

        Args:
            message (Message): message to react to
            bot (async_telebot.AsyncTeleBot): bot to react with

        """
        await bot.set_message_reaction(message.chat.id, message.message_id, [ReactionTypeEmoji("👍")])
    
    def _parse_input(self, message: Message, default_arg: str = "atr") -> dict[str, str]:
        """ parses the input message and returns a dictionary with the arguments and their values

        Args:
            message (Message): message to parse
            default_arg (str, optional): default argument name. Defaults to "atr".

        Raises:
            ValueError: if no arguments are provided

        Returns:
            dict[str, str]: dictionary with the arguments and their values

        """
        
        arguments = message.text.split()[1:]

        if len(arguments) == 0:
            raise ValueError("No arguments provided.")

        last_arg_name = default_arg
        parsed = {}

        if message.reply_to_message:
            reply_to_message = message.reply_to_message

            if reply_to_message.sticker:
                parsed['sticker_id'] = reply_to_message.sticker.file_id

            if reply_to_message.document and reply_to_message.document.mime_type == "video/mp4":
                parsed['document_id'] = reply_to_message.document.file_id

        for arg in arguments:
            if arg.startswith("—"):
                last_arg_name = arg.split("—")[1]
                parsed[last_arg_name] = ""
            elif arg.startswith("--"):
                last_arg_name = arg.split("--")[1]
                parsed[last_arg_name] = ""
            else:
                if last_arg_name not in parsed or parsed[last_arg_name] == "":
                    parsed[last_arg_name] = arg
                else:
                    parsed[last_arg_name] += " " + arg
        
        return parsed

    class StderrWriter:
        def __init__(self, log_event) -> None:
            self._log_event = log_event

        def write(self, message):
            if message.strip():
                self._log_event(message, Event_Type.ERROR)
        
        def flush(self):
            pass
    
    class StdoutWriter:
        def __init__(self, log_event) -> None:
            self._log_event = log_event

        def write(self, message):
            if message.strip():
                self._log_event(message, Event_Type.INFO)
        
        def flush(self):
            pass
    
    class LogHandler(logging.Handler):
        def __init__(self, log_event) -> None:
            super().__init__()
            self._log_event = log_event

        def emit(self, record):
            self._log_event(self.format(record), Event_Type.ERROR)