""" Telegram bot module """

import os
import importlib
from typing import TYPE_CHECKING
import logging
import dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext
from ..utils.database import Database
if TYPE_CHECKING:
    from .telebot_modules.base.base_module import BaseModule

class Telebot:
    """ Telebot instance """
    def __init__(self) -> None:
        self._config = dotenv.dotenv_values("dsb/telebot/.env")
        self._modules: dict[str, 'BaseModule'] = {}
        self._logger = logging.getLogger("DSB")
        self._logger.setLevel(logging.INFO)
        self._database = Database()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                        datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler("dsb/telebot.log")
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._handlers_path = "dsb/telebot/telebot_modules"
        self._ptb = ApplicationBuilder().token(self._config["telebot_token"]).build()
        self._ptb.add_error_handler(self._error_handler)
        self._commands = {}
        self._get_telebot_modules()

    @property
    def commands(self) -> dict:
        """ Returns the list of commands. """
        return self._commands

    @property
    def config(self) -> dict:
        """ Get the bot configuration """
        return self._config

    @property
    def database(self) -> 'Database':
        """ Get the database """
        return self._database

    def log(self, message: str) -> None:
        """ Log a message """
        self._logger.info(message)

    def error(self, message: str) -> None:
        """ Log an error """
        self._logger.error(message)

    def get_dsb_module(self, module_name: str) -> 'BaseModule':
        """ Get a DSB module by name """
        return self._modules.get(module_name, None)

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

    def get_telebot_module(self, module_name: str) -> 'BaseModule':
        """ Get a telebot module by name """
        return self._modules.get(module_name, None)

    async def _error_handler(self, update: Update, context: CallbackContext) -> None:
        """Log the error and send a message to the user."""
        if update is not None:
            self.error(context.error)
            await update.message.reply_text('An error occurred. Please try again later.')

    def run(self) -> bool:
        """ Run the module. Returns True if the module was run. """
        self._get_telebot_modules(reload=True)
        for name, module in self._modules.items():
            if module.prepare():
                self._commands.update(module.descriptions)
                module.add_handlers()
            else:
                print(f"Failed to load module {name}")
        self._ptb.run_polling()

if __name__ == "__main__":
    print("Running telebot")
    print("Logs will appear here")
    bot = Telebot()
    bot.run()
