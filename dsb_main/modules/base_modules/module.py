""" Base module to use as a base for creating new modules. """

from typing import TYPE_CHECKING
from dsb_main.modules.base_modules.statuses import Status
if TYPE_CHECKING:
    from dsb_main import dsb

def run_only(func):
    """ Decorator used to run a function only if the module is running. """
    def wrapper(self, *args, **kwargs):
        if self.running:
            return func(self, *args, **kwargs)
        return None
    return wrapper

class Module:
    """ Class used to create new modules. It needs to be named as the file
    using PascalCase for importing purposes."""
    name = "Module"
    def __init__(self, bot: 'dsb.DSB') -> None:
        self._status = Status.NOT_RUNNING
        self._bot = bot

    @property
    def status(self) -> Status:
        """ Get the status of the module. """
        return self._status

    @status.setter
    def status(self, status: Status) -> None:
        """ Set the status of the module. """
        self._status = status

    @property
    def running(self) -> bool:
        """ Check if the module is running. """
        return self._status == Status.RUNNING

    @property
    def error(self) -> bool:
        """ Check if the module is in error state. """
        return self._status == Status.ERROR

    def run(self) -> bool:
        """ Run the module. """
        self._status = Status.RUNNING
        self._bot.log("INFO", f"{self.name} module started")
        return True

    def stop(self) -> None:
        """ Stop the module. """
        self._status = Status.NOT_RUNNING
        self._bot.log("INFO", f"{self.name} module stopped")
