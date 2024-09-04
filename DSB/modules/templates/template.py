""" Template module for creating new modules. """

from argparse import Namespace
from DSB.modules.templates.statuses import Statuses

class Module:
    """ Class used to create new modules. It needs to be named the same as the file for importing purposes. """
    def __init__(self, bot) -> None:
        self.name = "Template"
        self.status = Statuses.NOT_RUNNING
        self.dependencies = []
        self.bot = bot

    def run(self, args: Namespace) -> None:
        """ Run the module. """
        for dependency in self.dependencies:
            if dependency not in self.bot:
                self.status = Statuses.WAITING
                return
        self.status = Statuses.RUNNING

    def stop(self) -> None:
        """ Stop the module. """
        self.status = Statuses.NOT_RUNNING