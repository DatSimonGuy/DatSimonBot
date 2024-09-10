""" Module used to create run logs. """

from datetime import datetime
from dsb_main.modules.base_modules.module import Module, run_only

class Logger(Module):
    """ Module used to create run logs. """
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self._name = "Logger"
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

    def run(self) -> bool:
        """ Run the module. Returns True if the module was run. """
        super().run()
        self.log("Logger started")
        return True

    def stop(self) -> None:
        """ Stop the module. """
        self.log("Logger stopping")
        super().stop()
