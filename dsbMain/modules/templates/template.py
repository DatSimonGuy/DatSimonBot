""" Template module for creating new modules. """

from argparse import Namespace
from dsbMain.modules.templates.statuses import Statuses

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
    def __init__(self, bot) -> None:
        self.name = "Template"
        self.status = Statuses.NOT_RUNNING
        self.dependencies = [] # List of module names that this module depends on
        self.bot = bot

    @property
    def running(self) -> bool:
        """ Check if the module is running. """
        return self.status == Statuses.RUNNING

    def get_dependencies(self, args: Namespace) -> None:
        """ Get the dependencies of the module. """
        self.status = Statuses.WAITING
        for dependency in self.dependencies:
            if not self.bot.run_module(dependency, args):
                self.status = Statuses.ERROR
                return

    def run(self, args: Namespace) -> bool: # pylint: disable=unused-argument
        """ Run the module. """
        if self.status == Statuses.ERROR:
            return False
        self.status = Statuses.RUNNING
        return True

    def stop(self) -> None:
        """ Stop the module. """
        self.status = Statuses.NOT_RUNNING
