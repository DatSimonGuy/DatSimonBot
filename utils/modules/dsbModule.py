import telebot.async_telebot as async_telebot
from telebot.types import Message, ReactionTypeEmoji
from ..types.databases.database import Database

class DsbModule:
    def __init__(self, bot: async_telebot.AsyncTeleBot) -> None:
        self._add_handlers(bot)
        self._commands = {

        }

    def _add_handlers(self, bot: async_telebot.AsyncTeleBot) -> None:
        for command, function in self._commands:
            bot.register_message_handler(function, commands=[command], pass_bot=True)
    
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
            else:
                if last_arg_name not in parsed or parsed[last_arg_name] == "":
                    parsed[last_arg_name] = arg
                else:
                    parsed[last_arg_name] += " " + arg
        
        return parsed
    
    