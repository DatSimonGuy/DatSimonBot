""" Module used to create run logs. """

from datetime import datetime
from DSB.modules.templates.template import Module

class Logger(Module):
    """ Module used to create run logs. """
    def __init__(self) -> None:
        super().__init__()
        self.name = "Logger"
        self.logs = []

    def log(self, message: str) -> None:
        """ Log a message. """
        self.logs.append(datetime.now().strftime("%d/%m %H:%M") + " " + message + "\n")

    def get_logs(self) -> list:
        """ Get the logs. """
        return self.logs

    def clear_logs(self) -> None:
        """ Clear the logs. """
        self.logs = []