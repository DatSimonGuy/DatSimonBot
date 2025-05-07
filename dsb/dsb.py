""" Main module of DSB """

import os
import time
import logging
import threading
import importlib
import dotenv
import schedule
import asyncio
from telegram import Update
from telegram.ext import Application, CallbackContext, ContextTypes
from dsb.data.database import Database
from dsb.types.module import BaseModule
from dsb.api.dsbapi import DSBApiThread
from dsb.types.errors import DSBError
from dsb.data.persistence import CustomPersistance
from dsb.types.handlers import AdminCommandHandler

class DSB:
    """ DatSimonBot - telegram app """
    def __init__(self):
        self._config = self.__get_env()
        self.database = Database()

        self._modules = []
        self._active_modules: dict[str, BaseModule] = {}
        self._api_task = DSBApiThread(self.database, self._config["api_port"])
        
        self._logger = self.__create_logger()
        
        self._scheduler = schedule.Scheduler()
        self._ticker_thread = threading.Thread(target=self.__ticker)
        self._stop_event = threading.Event()
        
        builder = Application.builder().token(self._config["token"])
        builder.persistence(CustomPersistance())
        builder.arbitrary_callback_data(True)
        
        self._app = builder.build()

        self._app.add_error_handler(self.__error_handler)
        self.__add_system_commands()

    @property
    def admins(self) -> list[int]:
        """ DSB admins """
        return self._config["admins"]

    @property
    def scheduler(self) -> schedule.Scheduler:
        """ DSB scheduler """
        return self._scheduler

    @property
    def logs(self) -> list[str]:
        """ Get the logs """
        with open("dsb.log", 'r', encoding="utf-8") as log_file:
            return log_file.readlines()

    async def __error_handler(self, update: Update, context: CallbackContext) -> None:
        """Log the error and send a message to the user."""
        self._logger.error("An error occurred: %s", context.error)
        if update.message is None:
            return
        if isinstance(context.error, DSBError):
            await update.message.reply_text(str(context.error))
        else:
            await update.message.reply_text('Unexpected error occured. Dev skill issue.')

    def __add_system_commands(self) -> None:
        self._app.add_handler(AdminCommandHandler(self, "reload", self.__reload_modules))
        self._app.add_handler(AdminCommandHandler(self, "quit", self.__quit_handler))

    def __ticker(self, tick_length: int = 1) -> None:
        """ Schedule timer """
        while not self._stop_event.is_set():
            self._scheduler.run_pending()
            time.sleep(tick_length)

    def __create_logger(self) -> logging.Logger:
        """ Create and set up logger """
        logger = logging.getLogger("DSB")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                        datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler("dsb.log")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def __get_env(self) -> dict:
        """ Load or prompt for environment variables. """
        if not os.path.exists(".env"):
            token = input("Telegram API token: ")
            admins = input("Bot admin IDs (space-separated): ")
            port = input("API port: ")
            with open(".env", "w", encoding="utf-8") as _:
                dotenv.set_key(".env", "token", token)
                dotenv.set_key(".env", "admins", admins.replace(" ", ","))
                dotenv.set_key(".env", "api_port", port)
        else:
            missing_keys = [key for key in ["token", "admins", "api_port"] if dotenv.get_key(".env", key) is None]
            if missing_keys:
                print(f"Missing keys in .env: {', '.join(missing_keys)}")
                exit(1)

        values = dotenv.dotenv_values(".env")
        values["admins"] = {int(admin) for admin in values["admins"].split(",")}
        return values

    def __load_modules(self) -> None:
        """ Load avaible modules """
        for module in os.listdir("dsb/modules"):
            if module.startswith("__"):
                continue
            module_name = module.replace(".py", "").title().replace("_", "")
            module_path = f"dsb.modules.{module.replace('.py', '')}"
            if module_name in self._active_modules:
                continue
            try:
                module = importlib.import_module(module_path)
                self._modules.append((module_name, module))
                module_class = getattr(module, module_name, None)
                if module_class is None or not issubclass(module_class, BaseModule):
                    continue
                module_instance = module_class(self._app, self)
            except Exception as e:
                print(f"Failed to load module {module_name}")
                self._logger.error("Failed to load module %s: %s", module_name, e)
                continue
            self._active_modules[module_name] = module_instance

    async def __reload_modules(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """ Reload modules during runtime """
        importlib.invalidate_caches()
        self.__disable_modules()
        self.__load_modules()
        message = ""
        for name, mod in self._modules:
            try:
                importlib.reload(mod)
                module_class = getattr(mod, name, None)
                module_instance = module_class(self._app, self)
            except Exception as e:
                message = f"{message}{name} failed to reload\n"
                self._logger.error("Failed to reload module %s: %s", name, e)
                continue
            self._active_modules[name] = module_instance
        self.__start_modules()
        await update.message.reply_text(f"Reloaded.\n{message}")

    def __start_modules(self) -> None:
        """ Start all modules """
        for module in self._active_modules.values():
            if module.prepare():
                module.add_handlers()
                continue
            self._logger.error("Failed to prepare module %s", module.__class__.__name__)

    def __disable_modules(self) -> None:
        """ Disable every module """
        for module in self._active_modules.values():
            module.remove_handlers()

    def __quit(self) -> None:
        self._stop_event.set()
        self._api_task.shutdown()
        self._api_task.join()
        self._ticker_thread.join()
        self._logger.info("DSB stopped")

    async def __quit_handler(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Bye.")
        self._app.stop_running()
        self.__quit()

    async def reload_data(self) -> None:
        """ Reload the data """
        self._app.bot_data = await self._app.persistence.get_bot_data()
        self._app.user_data = await self._app.persistence.get_user_data()
        self._app.chat_data = await self._app.persistence.get_chat_data()

    def set_value(self, key, value) -> None:
        """ Set bot data value """
        self._app.bot_data[key] = value
        event_loop = asyncio.get_event_loop()
        event_loop.create_task(self._app.persistence.update_bot_data(self._app.bot_data))

    def start(self) -> None:
        """ Start the app """
        self._ticker_thread.start()
        self._logger.info("DSB started")

        try:
            print("Starting...")
            self._api_task.start()
            print(f"Api running on port {self._config["api_port"]}")
            self.__load_modules()
            self.__start_modules()
            print("Finished loading.")
            self._app.run_polling()
        except KeyboardInterrupt:
            pass
        finally:
            self.__quit()
