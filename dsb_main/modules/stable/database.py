""" Database module for the DSB project. """

import os
import jsonpickle
from dsb_main.modules.base_modules.module import Module, run_only
from dsb_main.modules.stable.logger import Logger

class Database(Module):
    """ Database module for the DSB project. Will be rewritten to use SQL later. """
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self._name = "Database"
        self.dependencies = ["Logger"]
        self._logger: Logger = None
        self._directory = self._bot.config.get("database_location", "dsb_main/database")
        os.makedirs(self._directory, exist_ok=True)

    @run_only
    def save(self, data: dict, subdir: str, filename: str, unpickable: bool = True) -> bool:
        """ Save data to the database. """
        os.makedirs(f"{self._directory}/{subdir}", exist_ok=True)
        try:
            with open(f"{self._directory}/{subdir}/{filename}.json", "w", encoding='utf-8') as file:
                file.write(jsonpickle.encode(data, keys=True, indent=4, unpicklable=unpickable))
        except OSError:
            self._logger.log(f"Error saving data to {subdir}/{filename}")
            return False
        self._logger.log(f"Data saved to {subdir}/{filename}")
        return True

    @run_only
    def save_image(self, data: bytes, subdir: str, filename: str) -> None:
        """ Save image to the database. """
        os.makedirs(f"{self._directory}/{subdir}", exist_ok=True)
        with open(f"{self._directory}/{subdir}/{filename}.png", "wb") as file:
            file.write(data)
        self._logger.log(f"Image saved to {subdir}/{filename}")

    @run_only
    def load(self, subdir: str, filename: str) -> dict:
        """ Load data from the database. """
        try:
            with open(f"{self._directory}/{subdir}/{filename}.json", "r", encoding='utf-8') as file:
                data = jsonpickle.decode(file.read(), keys=True)
            self._logger.log(f"Data loaded from {subdir}/{filename}")
            return data
        except FileNotFoundError:
            self._logger.log(f"File {subdir}/{filename} not found")
            return {}

    @run_only
    def list_all(self, subdir: str) -> list:
        """ List all files in the directory. """
        try:
            return os.listdir(f"{self._directory}/{subdir}")
        except FileNotFoundError:
            self._logger.log(f"Directory {subdir} not found")
            return []

    @run_only
    def load_image(self, subdir: str, filename: str) -> bytes:
        """ Load image from the database. """
        try:
            with open(f"{self._directory}/{subdir}/{filename}.png", "rb") as file:
                data = file.read()
            self._logger.log(f"Image loaded from {subdir}/{filename}")
            return data
        except FileNotFoundError:
            self._logger.log(f"File {subdir}/{filename} not found")
            return b""

    @run_only
    def delete(self, subdir: str, filename: str) -> bool:
        """ Delete data from the database. """
        try:
            os.unlink(f"{self._directory}/{subdir}/{filename}.json")
            if not os.listdir(f"{self._directory}/{subdir}"):
                os.rmdir(f"{self._directory}/{subdir}")
            self._logger.log(f"Data deleted from {subdir}/{filename}")
            return True
        except FileNotFoundError:
            self._logger.log(f"File {subdir}/{filename} not found")
            return False

    @run_only
    def delete_image(self, subdir: str, filename: str) -> bool:
        """ Delete image from the database. """
        try:
            os.unlink(f"{self._directory}/{subdir}/{filename}.png")
            if not os.listdir(f"{self._directory}/{subdir}"):
                os.rmdir(f"{self._directory}/{subdir}")
            self._logger.log(f"Image deleted from {subdir}/{filename}")
            return True
        except FileNotFoundError:
            self._logger.log(f"File {subdir}/{filename} not found")
            return False

    def run(self) -> bool:
        """ Run the module. Returns True if the module was run. """
        super().run()
        self._logger = self._bot.get_module("Logger")
        self._logger.log("Database started")
        return True

    def stop(self) -> None:
        """ Stop the module. """
        super().stop()
        self._logger.log("Database stopped")
