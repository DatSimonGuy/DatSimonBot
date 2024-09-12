""" Module for lesson plan handling """

from dsb_main.modules.base_modules.module import Module, run_only
from dsb_main.modules.base_modules.statuses import Status
from dsb_main.modules.stable.database import Database
from dsb_main.modules.stable.logger import Logger
from .types.plan import Plan

class Planning(Module):
    """ Planning module """
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self._name = "Planning"
        self._logger: Logger = None
        self._db: Database = None
        self.dependencies = ["Logger", "Database"]

    @run_only
    def create_plan(self, name: str, group_id: int) -> bool:
        """ Create a new lesson plan """
        new_plan = Plan(name)
        return self._db.save(new_plan, f"{group_id}/plans", name)

    @run_only
    def get_plan(self, name: str, group_id: int) -> Plan:
        """ Get a lesson plan """
        return self._db.load(f"{group_id}/plans", name)

    @run_only
    def delete_plan(self, name: str, group_id: int) -> bool:
        """ Delete a lesson plan """
        return self._db.delete(f"{group_id}/plans", name)

    @run_only
    def get_plans(self, group_id: int) -> list:
        """ Get all lesson plans """
        return self._db.list_all(f"{group_id}/plans")

    @run_only
    def update_plan(self, name: str, group_id: int, new_plan: Plan) -> bool:
        """ Update a lesson plan """
        return self._db.save(new_plan, f"{group_id}/plans", name)

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
