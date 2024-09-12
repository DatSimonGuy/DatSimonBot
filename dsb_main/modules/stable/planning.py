""" Module for lesson plan handling """

from dsb_main.modules.base_modules.module import Module, run_only
from dsb_main.modules.base_modules.statuses import Status
from .types.plan import Plan, Lesson

class Planning(Module):
    """ Planning module """
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self._name = "Planning"
        self._logger = None
        self._db = None
        self.dependencies = ["Logger", "Database"]

    @run_only
    def create_plan(self, name: str) -> bool:
        """ Create a new lesson plan """
        return True

    def run(self) -> bool:
        """ Run the module. Returns True if the module was run. """
        super().run()
        self._logger = self._bot.get_module("Logger")
        self._db = self._bot.get_module("Database")

        if not self._db:
            self.status = Status.ERROR
            self._logger.log("Database module not found")
            return False

        if not self._logger:
            self.status = Status.ERROR
            return False

        self._logger.log("Planning module started")
        return True

    def stop(self) -> None:
        """ Stop the module. """
        super().stop()
        self._logger.log("Planning module stopped")
