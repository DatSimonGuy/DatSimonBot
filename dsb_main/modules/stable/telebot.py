""" Telegram bot module """

import os
import importlib
import asyncio
import threading
from telegram.ext import ApplicationBuilder
from dsb_main.modules.base_modules.module import Module

class Telebot(Module):
    """ Telebot instance """
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self._name = "Telebot"
        self.dependencies = ["Logger", "Database"]
        self._debug_mode = self._bot.config["debug"]
        self._logger = None
        self._db = None
        self._handlers_path = "dsb_main/modules/stable/telebot_modules"
        self._ptb = ApplicationBuilder().token(self._bot.config["telebot_token"]).build()
        self._bot_thread = None
        self._loop = asyncio.new_event_loop()
        self._get_telebot_modules()

    @property
    def debug(self) -> bool:
        """ Returns the debug mode status. """
        return self._debug_mode

    def _get_telebot_modules(self) -> None:
        """ Loads handlers from files """
        for module_file in os.listdir(self._handlers_path):
            if module_file.endswith(".py") and module_file != "__init__.py":
                module_name = module_file[:-3]
                module = importlib.import_module(
                        f"{self._handlers_path.replace('/', '.')}.{module_name}")
                module_name = module_name.title().replace("_", "")
                module = getattr(module, module_name)
                module(self._ptb)

    def _run_bot(self):
        asyncio.set_event_loop(self._loop)
        self._ptb.run_polling(close_loop=False)

    def run(self) -> bool:
        """ Run the module. Returns True if the module was run. """
        super().run()
        self._bot_thread = threading.Thread(target=self._run_bot)
        self._bot_thread.start()
        self._logger = self._bot.get_module("Logger")
        self._db = self._bot.get_module("Database")
        self._logger.log("Telebot started")
        return True

    def stop(self) -> None:
        """ Stop the module and the bot cleanly. """
        super().stop()
        self._loop.call_soon_threadsafe(self._ptb.stop_running)
        asyncio.run_coroutine_threadsafe(self._ptb.shutdown(), self._loop)
        self._bot_thread.join()
        self._logger.log("Telebot stopped")
