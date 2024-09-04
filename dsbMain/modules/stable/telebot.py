""" Telebot module. """

from dsbMain.modules.templates.template import Module
from dsbMain.modules.templates.statuses import Statuses
from dsbMain import dsb

class Telebot(Module):
    """ Telebot instance """
    def __init__(self, bot: dsb.DSB) -> None:
        super().__init__(bot)
        self.name = "Telebot"
        self.dependencies = ["Logger"]
        self._logger = None

    def run(self, _) -> None:
        """ Run the module. """
        self.status = Statuses.RUNNING
        self._logger = self.bot.get_module("Logger")
        self._logger.log("Telebot started")

    def stop(self) -> None:
        """ Stop the module. """
        self.status = Statuses.NOT_RUNNING
        self._logger.log("Telebot stopped")
