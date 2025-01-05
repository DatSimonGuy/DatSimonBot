""" The engine for dsb v2 """

import os
import time
import asyncio
import logging
import threading
import importlib.util
from typing import Any
import requests
from telegram import Update
from telegram.ext import Application, CallbackContext, InvalidCallbackData
import rich.console
import rich.progress
import psutil
import schedule
from dotenv import dotenv_values, set_key
from dsb.types.module import BaseModule
from dsb.types.persistence import CustomPersistance
from dsb.types.errors import DSBError

class DSBEngine:
    """ Engine for DatSimonBot """
    def __init__(self) -> None:
        # Environment variables
        self.__create_dotenv()
        self._config = dotenv_values(".env")
        self._config = self.__parse_config(self._config)

        # Modules
        self._modules: dict[str, BaseModule] = {}

        # Memory and CPU usage
        self._process = psutil.Process()
        self._cpu_usage = 0.0
        self._memory_usage = 0.0

        # Logger
        self._logger = logging.getLogger("DSB")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                        datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler("dsb.log")
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

        # Scheduler for the engine
        self._scheduler = schedule.Scheduler()
        self._ticker_thread = threading.Thread(target=self.__ticker)
        self._stop_event = threading.Event()

        # Checking environment variables
        if self._config["telebot_token"] == "<token>":
            error_message = "Please replace the <token> in .env file with your telegram bot token"
            self._logger.error(error_message)
            raise ValueError(error_message)
        if not os.path.exists(self._config["module_src"]):
            error_message = f"Module source directory {self._config['module_src']} does not exist"
            self._logger.error(error_message)
            raise FileNotFoundError(error_message)

        # Building the application
        builder = Application.builder().token(self._config["telebot_token"])
        builder.persistence(CustomPersistance())
        builder.arbitrary_callback_data(True)
        self._app = builder.build()

        # Error handler
        self._app.add_error_handler(self.__error_handler)

    @property
    def admins(self) -> list[int]:
        """ Get the list of admins """
        return self._config["admins"]

    @property
    def scheduler(self) -> schedule.Scheduler:
        """ Get the scheduler """
        return self._scheduler

    @property
    def logs(self) -> list[str]:
        """ Get the logs """
        with open("dsb.log", 'r', encoding="utf-8") as log_file:
            return log_file.readlines()

    @property
    def config(self) -> dict[str, Any]:
        """ Get the configuration """
        return self._config

    def __parse_config(self, config: dict[str, str]) -> dict[str, Any]:
        """ Parse the environment variables """
        try:
            config["admins"] = list(map(int, config["admins"].split(",")))
        except ValueError:
            config["admins"] = []
        config["experimental"] = config["experimental"].lower() == "true"
        return config

    def __ticker(self, tick_length: int = 1) -> None:
        """ Schedule timer """
        while not self._stop_event.is_set():
            self._cpu_usage = self._process.cpu_percent()
            self._memory_usage = self._process.memory_info().rss / 1024 ** 2
            self._scheduler.run_pending()
            time.sleep(tick_length)

    def __show_status(self, console: rich.console.Console) -> None:
        """ Show the status of the engine"""
        status_text = "[bold green]DSB Engine is running...[/bold green]"
        with console.status(status_text, spinner="dots") as status:
            while not self._stop_event.is_set():
                cpu_usage_str = f"CPU: [bold blue]{self._cpu_usage:.2f}%[/bold blue]"
                memory_usage_str = f"Memory: [bold blue]{self._memory_usage:.2f}[/bold blue] MB"
                status.update(status_text + f"\n{cpu_usage_str} {memory_usage_str}")
                time.sleep(1)

    async def __error_handler(self, update: Update, context: CallbackContext) -> None:
        """Log the error and send a message to the user."""
        self._logger.error("An error occurred: %s", context.error)
        if isinstance(context.error, DSBError) and update.message is not None:
            await update.message.reply_text(str(context.error))
        elif isinstance(context.error, DSBError):
            await context.bot.send_message(update.effective_chat.id, str(context.error))
        elif update.message is not None:
            await update.message.reply_text('An error occurred. Please try again later.')

    def __check_internet_connection(self) -> bool:
        """ Check if the internet connection is available """
        try:
            requests.get("https://google.com", timeout=1)
            return True
        except requests.ConnectionError:
            return False

    def __create_dotenv(self) -> None:
        if not os.path.exists(".env"):
            config_values = {
                "telebot_token": "<token>",
                "admins": "<admin1>,<admin2>",
                "module_src": "dsb/modules",
                "experimental": "False",
                "database_path": "dsb/database",
            }
            with open(".env", "w", encoding="utf-8"):
                pass
            for key, value in config_values.items():
                set_key(".env", key, value)

    def __load_modules(self, console: rich.console.Console) -> tuple[int, int]:
        """ Load modules from a directory """
        success = 0
        modules_to_load = []
        for dir_path, _, modules in os.walk(self._config["module_src"]):
            for module in modules:
                if dir_path.endswith("experimental") and not self._config["experimental"]:
                    continue
                if module.startswith("__"):
                    continue
                if dir_path.endswith("__"):
                    continue
                modules_to_load.append((dir_path, module))

        console.print(f"[bold yellow]Found {len(modules_to_load)} modules[/bold yellow]")

        with rich.progress.Progress(
            "[progress.description]{task.fields[module]}",
            rich.progress.BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            rich.progress.TimeRemainingColumn(),
            ) as progress:
            task = progress.add_task("Loading modules...", total=len(modules_to_load), module="")
            for dir_path, module in modules_to_load:
                module_name = module.replace(".py", "").title().replace("_", "")
                progress.update(task, module=f"Loading {module_name}...")
                module_path = os.path.join(dir_path, module.replace(".py", ""))
                module_path = module_path.replace("/", ".").replace("\\", ".")
                mod = importlib.import_module(module_path)
                module_class = getattr(mod, module_name, None)
                if module_class is None or not issubclass(module_class, BaseModule):
                    continue
                try:
                    module_instance = module_class(self._app, self)
                except Exception as e: # pylint: disable=broad-except
                    self._logger.error("Failed to load module %s: %s", module_name, e)
                    progress.advance(task)
                    continue
                self._modules[module_name] = module_instance
                success += 1
                progress.advance(task)
        return success, len(modules_to_load) - success

    async def reload_data(self) -> None:
        """ Reload the data """
        self._app.bot_data = await self._app.persistence.get_bot_data()
        self._app.user_data = await self._app.persistence.get_user_data()
        self._app.chat_data = await self._app.persistence.get_chat_data()
        self._app.callback_data = await self._app.persistence.get_callback_data()

    def set_value(self, key, value) -> None:
        """ Set bot data value """
        self._app.bot_data[key] = value
        event_loop = asyncio.get_event_loop()
        event_loop.create_task(self._app.persistence.update_bot_data(self._app.bot_data))

    def start_modules(self) -> tuple[int, int]:
        """ Start all modules """
        success, fail = 0, 0
        for module in self._modules.values():
            if module.prepare():
                module.add_handlers()
                success += 1
            else:
                self._logger.error("Failed to prepare module %s", module.__class__.__name__)
                fail += 1
        return success, fail

    def start(self) -> None:
        """ Start the engine """
        if not self.__check_internet_connection():
            print("No internet connection. Exiting...")
            self._logger.error("No internet connection. Start failed")
            return

        self._ticker_thread.start()
        console = rich.console.Console()
        self._logger.info("DSB Engine started!")

        try:
            console.print("[bold green]DSB Engine started[/bold green]")
            success, fail = self.__load_modules(console)
            if fail > 0:
                console.print(f"[bold yellow]Loaded {success} modules,"+\
                              f" {fail} failed to load[/bold yellow]")
            else:
                console.print(f"[bold green]Loaded {success} modules[/bold green]")
            console.print("[bold yellow]Starting modules...[/bold yellow]")
            success, fail = self.start_modules()
            if fail > 0:
                console.print(f"[bold yellow]Started {success} modules,"+\
                              f" {fail} failed to start[/bold yellow]")
            else:
                console.print(f"[bold green]Started {success} modules[/bold green]")
            status_thread = threading.Thread(target=self.__show_status, args=(console,))
            status_thread.start()
            self._app.run_polling()
        except KeyboardInterrupt:
            pass
        finally:
            self._stop_event.set()
            self._ticker_thread.join()
            status_thread.join()
            self._logger.info("DSB Engine stopped!")
            console.print("\n[bold red]DSB Engine stopped![/bold red]")
