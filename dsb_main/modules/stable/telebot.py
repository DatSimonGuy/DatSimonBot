""" Telegram bot module """

import os
import importlib
import asyncio
import threading
from typing import TYPE_CHECKING, Literal
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext
from dsb_main.modules.base_modules.module import Module
from dsb_main.modules.base_modules.statuses import Status
if TYPE_CHECKING:
    from .telebot_modules.base.base_module import BaseModule

class Telebot(Module):
    """ Telebot instance """
    name = "Telebot"
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self._modules: dict[str, 'BaseModule'] = {}
        self._handlers_path = "dsb_main/modules/stable/telebot_modules"
        self._ptb = ApplicationBuilder().token(self._bot.config["telebot_token"]).build()
        self._ptb.add_error_handler(self._error_handler)
        self._commands = {}
        self._bot_thread = None
        self._loop = asyncio.new_event_loop()
        self._chat_macros = {}
        self._get_telebot_modules()

    @property
    def commands(self) -> dict:
        """ Returns the list of commands. """
        return self._commands

    @property
    def config(self) -> dict:
        """ Get the bot configuration """
        return self._bot.config

    @property
    def chat_macros(self) -> dict:
        """ Get the chat macros """
        return self._chat_macros

    def log(self, level: Literal["ERROR", "INFO", "WARNING", "DEBUG"],
            message: str) -> None:
        """ Log a message """
        self._bot.log(level, message)

    def _get_telebot_modules(self, reload: bool = False) -> None:
        """ Loads handlers from files, optionally reloading them """
        self._modules.clear()
        for module_file in os.listdir(self._handlers_path):
            if module_file.endswith(".py") and module_file != "__init__.py":
                module_name = module_file[:-3]
                if reload:
                    module = importlib.reload(importlib.import_module(
                        f"{self._handlers_path.replace('/', '.')}.{module_name}"))
                else:
                    module = importlib.import_module(
                        f"{self._handlers_path.replace('/', '.')}.{module_name}")
                module_name = module_name.title().replace("_", "")
                module = getattr(module, module_name)
                new_module: 'BaseModule' = module(self._ptb, self)
                self._modules[module_name] = new_module

    def get_dsb_module(self, module_name: str) -> Module:
        """ Get a DSB module by name """
        return self._bot.get_module(module_name)

    def get_telebot_module(self, module_name: str) -> 'BaseModule':
        """ Get a telebot module by name """
        return self._modules.get(module_name, None)

    async def _error_handler(self, update: Update, context: CallbackContext) -> None:
        """Log the error and send a message to the user."""
        self._bot.log("ERROR", "Exception while handling an update:", exc_info=context.error)
        if update is not None:
            await update.message.reply_text('An error occurred. Please try again later.')

    def send_message(self, chat_id: int, message: str) -> None:
        """ Send a message to a chat """
        if chat_id in self._chat_macros:
            chat_id = self._chat_macros[chat_id]
        try:
            if isinstance(chat_id, str):
                chat_id = int(chat_id)
        except ValueError:
            self._bot.log("ERROR", f"Invalid chat id {chat_id}")
            return
        asyncio.run_coroutine_threadsafe(self._ptb.bot.send_message(chat_id, message), self._loop)

    def send_image(self, chat_id: int, image: bytes, caption: str = "") -> None:
        """ Send an image to a chat """
        if chat_id in self._chat_macros:
            chat_id = self._chat_macros[chat_id]
        try:
            if isinstance(chat_id, str):
                chat_id = int(chat_id)
        except ValueError:
            self._bot.log("ERROR", f"Invalid chat id {chat_id}")
            return
        asyncio.run_coroutine_threadsafe(self._ptb.bot.send_photo(chat_id, image, caption=caption),
                                         self._loop)

    def download_file(self, file_id: str) -> bytes:
        """ Download a file from the bot """
        file = asyncio.run_coroutine_threadsafe(self._ptb.bot.getFile(file_id),
                                                self._loop).result()
        return asyncio.run_coroutine_threadsafe(file.download_as_bytearray(),
                                                self._loop).result()

    def get_chat_id(self, macro: str) -> int:
        """ Get the chat id from a chat macro """
        return self._chat_macros.get(macro, -1)

    def add_chat_macro(self, chat_id: int, macro: str) -> None:
        """ Add a chat macro """
        self._chat_macros[macro] = chat_id
        database = self._bot.get_module("Database")
        if database:
            database.save(self._chat_macros, "telebot", "chat_macros")

    def remove_chat_macro(self, macro: str) -> None:
        """ Remove a chat macro """
        self._chat_macros.pop(macro, None)
        database = self._bot.get_module("Database")
        if database:
            database.save(self._chat_macros, "telebot", "chat_macros")

    def _run_bot(self):
        asyncio.set_event_loop(self._loop)
        self._ptb.run_polling(close_loop=False)

    def run(self) -> bool:
        """ Run the module. Returns True if the module was run. """
        if self._status == Status.RUNNING:
            return True
        database = self._bot.get_module("Database")
        if database:
            self._chat_macros = database.load("telebot", "chat_macros")
        else:
            self._chat_macros = {}
        self._get_telebot_modules(reload=True)
        for name, module in self._modules.items():
            if module.prepare():
                self._commands.update(module.descriptions)
                module.add_handlers()
            else:
                self._bot.log("ERROR", f"Failed to prepare module {name}")
        self._bot_thread = threading.Thread(target=self._run_bot)
        self._bot_thread.start()
        return super().run()

    def stop(self) -> None:
        """ Stop the module and the bot cleanly. """
        for module in self._modules.values():
            module.remove_handlers()
        self._loop.call_soon_threadsafe(self._ptb.stop_running)
        asyncio.run_coroutine_threadsafe(self._ptb.shutdown(), self._loop)
        self._bot_thread.join()
        super().stop()
