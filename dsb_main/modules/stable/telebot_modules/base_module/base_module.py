""" telegram bot base module """

from telegram.ext import CommandHandler

class BaseModule:
    """ Base module for all telegram bot modules. """
    def __init__(self, bot) -> None:
        self._ptb = bot
        self._handlers = {}

    def add_handlers(self) -> None:
        """ Add handlers to the dispatcher """
        for command, handler in self._handlers.items():
            self._ptb.add_handler(CommandHandler(command, handler))

    def remove_handlers(self) -> None:
        """ Remove handlers from the dispatcher """
        for command, handler in self._handlers.items():
            self._ptb.remove_handler(CommandHandler(command, handler))
