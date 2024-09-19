""" Database module for the DSB project. """

import os
from typing import Any
import jsonpickle
from dsb_main.modules.base_modules.module import Module

class Database(Module):
    """ Database module for the DSB project. Will be rewritten to use SQL later. """
    name = "Database"
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self._directory = self._bot.config.get("database_location", "dsb_main/database")
        os.makedirs(self._directory, exist_ok=True)

    def save(self, data: dict, subdir: str, filename: str, unpickable: bool = True) -> bool:
        """ Save data to the database. """
        os.makedirs(f"{self._directory}/{subdir}", exist_ok=True)
        try:
            with open(f"{self._directory}/{subdir}/{filename}.json", "w", encoding='utf-8') as file:
                file.write(jsonpickle.encode(data, keys=True, indent=4, unpicklable=unpickable))
        except OSError:
            self._bot.log("ERROR", f"Error saving data to {subdir}/{filename}")
            return False
        self._bot.log("DEBUG", f"Data saved to {subdir}/{filename}")
        return True

    def save_image(self, data: bytes, subdir: str, filename: str) -> bool:
        """ Save image to the database. """
        os.makedirs(f"{self._directory}/{subdir}", exist_ok=True)
        try:
            with open(f"{self._directory}/{subdir}/{filename}.png", "wb") as file:
                file.write(data)
        except OSError:
            self._bot.log("ERROR", f"Error saving image to {subdir}/{filename}")
            return False
        self._bot.log("DEBUG", f"Image saved to {subdir}/{filename}")
        return True

    def load(self, subdir: str, filename: str, default: Any = None) -> dict:
        """ Load data from the database. """
        try:
            with open(f"{self._directory}/{subdir}/{filename}.json", "r", encoding='utf-8') as file:
                data = jsonpickle.decode(file.read(), keys=True)
            self._bot.log("DEBUG", f"Data loaded from {subdir}/{filename}")
            return data
        except FileNotFoundError:
            self._bot.log("DEBUG", f"File {subdir}/{filename} not found")
            if default is None:
                return {}
            return default

    def list_all(self, subdir: str) -> list:
        """ List all files in the directory. """
        try:
            return os.listdir(f"{self._directory}/{subdir}")
        except FileNotFoundError:
            self._bot.log("DEBUG", f"Directory {subdir} not found")
            return []

    def load_image(self, subdir: str, filename: str) -> bytes:
        """ Load image from the database. """
        try:
            with open(f"{self._directory}/{subdir}/{filename}.png", "rb") as file:
                data = file.read()
            self._bot.log("DEBUG", f"Image loaded from {subdir}/{filename}")
            return data
        except FileNotFoundError:
            self._bot.log("DEBUG", f"File {subdir}/{filename} not found")
            return b""

    def delete(self, subdir: str, filename: str) -> bool:
        """ Delete data from the database. """
        try:
            os.unlink(f"{self._directory}/{subdir}/{filename}.json")
            if not os.listdir(f"{self._directory}/{subdir}"):
                os.rmdir(f"{self._directory}/{subdir}")
            self._bot.log("DEBUG", f"Data deleted from {subdir}/{filename}")
            return True
        except FileNotFoundError:
            self._bot.log("DEBUG", f"File {subdir}/{filename} not found")
            return False

    def delete_image(self, subdir: str, filename: str) -> bool:
        """ Delete image from the database. """
        try:
            os.unlink(f"{self._directory}/{subdir}/{filename}.png")
            if not os.listdir(f"{self._directory}/{subdir}"):
                os.rmdir(f"{self._directory}/{subdir}")
            self._bot.log("DEBUG", f"Image deleted from {subdir}/{filename}")
            return True
        except FileNotFoundError:
            self._bot.log("DEBUG", f"File {subdir}/{filename} not found")
            return False
