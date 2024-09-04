""" Database module for the DSB project. """

import os
import jsonpickle
from dsbMain.modules.templates.template import Module, run_only
from dsbMain.modules.templates.statuses import Statuses
from dsbMain import dsb

class Database(Module):
    """ Database module for the DSB project. Will be rewritten to use SQL later. """
    def __init__(self, bot: dsb.DSB) -> None:
        super().__init__(bot)
        self.name = "Database"
        self.dependencies = ["Logger"]
        self._logger = None
        self._directory = "dsbMain/data"

    @run_only
    def save(self, data: dict, subdir: str, filename: str) -> None:
        """ Save data to the database. """
        os.makedirs(f"{self._directory}/{subdir}", exist_ok=True)
        with open(f"{self._directory}/{subdir}/{filename}.json", "w", encoding='utf-8') as file:
            file.write(jsonpickle.encode(data, keys=True, unpicklable=False, indent=4))
        self._logger.log(f"Data saved to {subdir}/{filename}")

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
    def delete(self, subdir: str, filename: str) -> None:
        """ Delete data from the database. """
        try:
            os.unlink(f"{self._directory}/{subdir}/{filename}.json")
            if not os.listdir(f"{self._directory}/{subdir}"):
                os.rmdir(f"{self._directory}/{subdir}")
            self._logger.log(f"Data deleted from {subdir}/{filename}")
        except FileNotFoundError:
            self._logger.log(f"File {subdir}/{filename} not found")

    def run(self, _) -> None:
        """ Run the module. """
        self.status = Statuses.RUNNING
        self._logger = self.bot.get_module("Logger")
        self._logger.log("Database started")

    def stop(self) -> None:
        """ Stop the module. """
        self.status = Statuses.NOT_RUNNING
        self._logger.log("Database stopped")
