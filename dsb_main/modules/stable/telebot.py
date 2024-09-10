""" Telebot module. """

from dsb_main.modules.base_modules.module import Module

class Telebot(Module):
    """ Telebot instance """
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self._name = "Telebot"
        self.dependencies = ["Logger", "Database"]
        self._logger = None

    def run(self) -> bool:
        """ Run the module. Returns True if the module was run. """
        super().run()
        self._logger = self._bot.get_module("Logger")
        self._logger.log("Telebot started")
        return True

    def stop(self) -> None:
        """ Stop the module. """
        super().stop()
        self._logger.log("Telebot stopped")
