""" Base mode class for all modes. """

from rich.console import Console
from dsb_main.dsb import DSB

class BaseMode:
    """ Base mode class for all modes. """
    def __init__(self, bot: DSB, console: Console) -> None:
        self._bot = bot
        self._console = console
        self._commands = {}

    @property
    def commands(self) -> dict:
        """ Returns the list of commands. """
        return self._commands

    def display(self) -> None:
        """ Display the mode. """
        raise NotImplementedError
