""" Module for lesson plan handling """

from dsb_main.modules.base_modules.module import Module, run_only
from dsb_main.modules.stable.database import Database
from .types.plan import Plan

class Planning(Module):
    """ Planning module """
    name = "Planning"
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self._db: Database = None

    @run_only
    def create_plan(self, name: str, group_id: int) -> bool:
        """ Create a new lesson plan """
        new_plan = Plan(name)
        return self._db.save(new_plan, f"{group_id}/plans", name)

    @run_only
    def get_plan(self, name: str, group_id: int) -> Plan | None:
        """ Get a lesson plan """
        return self._db.load(f"{group_id}/plans", name)

    @run_only
    def delete_plan(self, name: str, group_id: int) -> bool:
        """ Delete a lesson plan """
        return self._db.delete(f"{group_id}/plans", name)

    @run_only
    def get_plans(self, group_id: int) -> list:
        """ Get all lesson plans """
        plan_list =  self._db.list_all(f"{group_id}/plans")
        plan_list = [plan[:-5] for plan in plan_list]
        return plan_list

    @run_only
    def update_plan(self, name: str, group_id: int, new_plan: Plan, new_name: str = "") -> bool:
        """ Update a lesson plan """
        if new_name:
            self._db.delete(f"{group_id}/plans", name)
            return self._db.save(new_plan, f"{group_id}/plans", new_name)
        return self._db.save(new_plan, f"{group_id}/plans", name)

    @run_only
    def who_is_free(self, group_id: int) -> list[tuple[str, str]]:
        """ Get a list of students who are free at a given time and seconds to the next lesson """
        plans = self.get_plans(group_id)
        if not plans:
            return []
        free_students = []
        for plan in plans:
            plan = self.get_plan(plan, group_id)
            if plan.is_free():
                next_lesson = plan.next_lesson
                if not next_lesson:
                    time_diff = "No lessons left"
                else:
                    diff = next_lesson.time_until.total_seconds()
                    time_diff = f"{diff // 3600}:{(diff % 3600) // 60}"
                for student in plan.students:
                    free_students.append((student, time_diff))
        return free_students

    def run(self) -> bool:
        """ Run the module. Returns True if the module was run. """
        self._db = self._bot.get_module("Database")
        if not self._db:
            self._bot.log("ERROR", "Database module not found")
            return False
        return super().run()
