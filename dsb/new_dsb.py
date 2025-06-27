import dotenv
import os
import logging
import schedule
import threading
import time
from dsb.data.new_database import Database
from telegram import Update
from telegram.ext import Application, CallbackContext
from dsb.types.errors import DSBError

ENV_PATH = ".env"
DATABASE_PATH = "dsb/database"

class DSB:
    """ DatSimonBot class """
    def __init__(self):
        self._config = self.__get_env()
        self.database = Database(DATABASE_PATH)
        
        self._logger = self.__create_logger()
        
        self._scheduler = schedule.Scheduler()
        self._ticker_thread = threading.Thread(target=self.__ticker)
        self._stop_event = threading.Event()
        
        builder = Application.builder().token(self._config["token"])
        builder.persistence(self.database.persistance)
        builder.arbitrary_callback_data(True)
        
        self._app = builder.build()
        self._app.add_error_handler(self.__error_handler)
        
    def __ticker(self, tick_length: int = 1) -> None:
        """ Schedule timer """
        while not self._stop_event.is_set():
            self._scheduler.run_pending()
            time.sleep(tick_length)

    def __get_env(self) -> dict:
        """ Load or prompt for environment variables. """
        required_values = {
            "token": "Telegram API token: ",
            "bot admins": "Bot admin IDs (space-separated): ",
        }
        
        if not os.path.exists(ENV_PATH):
            with open(ENV_PATH, "w") as f:
                f.write("# DSB configuration file")

        config = dotenv.dotenv_values(ENV_PATH)
        for name, input_prompt in required_values.items():
            if name in config:
                continue

            val = input(input_prompt)
            dotenv.set_key(ENV_PATH, name, val)
            config[name] = val
        
        return config

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

    async def __error_handler(self, update: Update, context: CallbackContext) -> None:
        """Log the error and send a message to the user."""
        self._logger.error("An error occurred: %s", context.error)
        if update.message is None:
            return
        if isinstance(context.error, DSBError):
            await update.message.reply_text(str(context.error))
        else:
            await update.message.reply_text('Someone tell soy there\'s a problem with his bot')