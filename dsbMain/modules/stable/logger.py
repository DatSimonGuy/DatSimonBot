""" Module used to create run logs. """

from datetime import datetime
from dsbMain.modules.templates.template import Module, run_only
from dsbMain.modules.templates.statuses import Statuses
from dsbMain import dsb

class Logger(Module):
    """ Module used to create run logs. """
    def __init__(self, bot: dsb.DSB) -> None:
        super().__init__(bot)
        self.name = "Logger"
        self.logs = []
        self.dependencies = []
        self.action = None

    @run_only
    def log(self, message: str) -> None: # pylint: disable=method-hidden
        """ Log a message. """
        if self.action is not None:
            self.action(message)
        else:
            self.logs.append(datetime.now().strftime("%d/%m %H:%M") + " " + message + "\n")

    def get_logs(self) -> list:
        """ Get the logs. """
        return self.logs

    def clear_logs(self) -> None:
        """ Clear the logs. """
        self.logs = []

    def run(self, _) -> None:
        """ Run the module. """
        self.status = Statuses.RUNNING
        self.log("Logger started")

    def stop(self) -> None:
        """ Stop the module. """
        self.log("Logger stopping")
        self.status = Statuses.NOT_RUNNING
