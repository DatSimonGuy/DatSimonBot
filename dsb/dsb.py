""" Telegram bot module """

import os
import time
import importlib
from typing import TYPE_CHECKING, Generator
import logging
import threading
import dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
import schedule
from .types.database import Database
from .types.module import admin_only
if TYPE_CHECKING:
    from .types.module import BaseModule

class DSB:
    """ DatSimonBot main class """
    def __init__(self, *, module_src: str, experimental: bool = False) -> None:
        self._config = dotenv.dotenv_values(".env")
        self._modules: dict[str, dict[str, 'BaseModule']] = {}
        self._logger = logging.getLogger("DSB")
        self.__loger_setup()
        self._database = Database()
        self._module_dir = module_src
        self._experimental = experimental
        self._bot = ApplicationBuilder().token(self._config["telebot_token"]).build()
        self._bot.add_error_handler(self._error_handler)
        self._commands = {
            "switch_mode": "Switch the bot mode"
        }
        self._scheduler = schedule.Scheduler()
        self._schedule_thread = threading.Thread(target=self.__schedule_timer)
        self._schedule_thread.start()
        self._bot.add_handler(CommandHandler("switch_mode", self._switch_mode))
        self.__load_modules()

    def __schedule_timer(self) -> None:
        is_running = threading.Event().is_set
        while is_running():
            self._scheduler.run_pending()
            time.sleep(1)

    def __loger_setup(self):
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                        datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler("dsb.log")
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    @property
    def scheduler(self) -> schedule.Scheduler:
        """ Get the scheduler """
        return self._scheduler

    @property
    def experimental(self) -> bool:
        """ Get experimental mode """
        return self._experimental

    @property
    def commands(self) -> dict:
        """ Get bot command list """
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

    @admin_only
    async def _switch_mode(self, update: Update, _) -> None:
        """ Switch the bot mode """
        if not self._experimental:
            self._experimental = True
            self.__load_modules(reload=True)
            await update.message.reply_text("Experimental mode enabled")
        else:
            self._experimental = False
            self.__load_modules(reload=True)
            await update.message.reply_text("Experimental mode disabled")

    def __load_dir(self, path: str, reload: bool = False) \
        -> Generator[tuple[str, 'BaseModule'], None, None]:
        for module_file in os.listdir(path):
            if module_file.endswith(".py") and module_file != "__init__.py":
                module_name = module_file[:-3]
                try:
                    if reload:
                        module = importlib.reload(importlib.import_module(
                            f"{path.replace('/', '.')}.{module_name}"))
                    else:
                        module = importlib.import_module(
                            f"{path.replace('/', '.')}.{module_name}")
                except ImportError:
                    self.error(f"Failed to load module {module_name}")
                    continue
                module_name = module_name.title().replace("_", "")
                module = getattr(module, module_name)
                new_module: 'BaseModule' = module(self._bot, self)
                yield module_name, new_module

    def __load_modules(self, reload: bool = False) -> None:
        """ Loads handlers from files, optionally reloading them """
        self._modules.clear()

        self._modules["stable"] = {}
        self._modules["experimental"] = {}

        for module_type in ["stable", "experimental"]:
            modules_info = self.__load_dir(os.path.join(self._module_dir, module_type), reload)
            for name, module in modules_info:
                self._modules[module_type][name] = module

    def get_module(self, module_name: str) -> 'BaseModule':
        """ Get a telebot module by name """
        return self._modules.get(module_name, None)

    async def _error_handler(self, update: Update, context: CallbackContext) -> None:
        """Log the error and send a message to the user."""
        if update is not None:
            self.error(context.error)
            await update.message.reply_text('An error occurred. Please try again later.')

    def run(self) -> None:
        """ Run the telebot """
        print("Starting telebot")
        self.__load_modules(reload=True)
        modules = self._modules["stable"]
        if self._experimental:
            modules.update(self._modules["experimental"])
        for name, module in modules.items():
            if module.prepare():
                self._commands.update(module.descriptions)
                module.add_handlers()
            else:
                print(f"Failed to prepeare module {name}")
        try:
            print("Modules loaded")
            self._bot.run_polling()
        except KeyboardInterrupt:
            threading.Event().set()
            self._schedule_thread.join()
        self._logger.info("Telebot stopped")
