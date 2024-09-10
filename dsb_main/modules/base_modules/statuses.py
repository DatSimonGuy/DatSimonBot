""" This module contains the statuses for the modules. """

from enum import Enum

class Status(Enum):
    """ Enum containing the statuses for the modules. """
    NOT_RUNNING = ("Not running", 0)
    RUNNING = ("Running", 2)
    ERROR = ("Error", 0)
    WARNING = ("Warning", 1)
    SUCCESS = ("Success", 2)
    CLOSING = ("Closing", 1)
    WAITING = ("Waiting", 1)
