""" Module for lesson plan handling """

from dsb.utils.database import Database
from dsb.types.plan import Plan

class Planning:
    """ Class for lesson plan handling """
    def __init__(self, database: Database = Database()) -> None:
        self._db = database

    def create_plan(self, name: str, group_id: int) -> bool:
        """ Create a new lesson plan """
        new_plan = Plan(name)
        return self._db.save(new_plan, f"{group_id}/plans", name)

    def get_plan(self, name: str, group_id: int) -> Plan | None:
        """ Get a lesson plan """
        return self._db.load(f"{group_id}/plans", name)

    def delete_plan(self, name: str, group_id: int) -> bool:
        """ Delete a lesson plan """
        return self._db.delete(f"{group_id}/plans", name)

    def get_plans(self, group_id: int) -> list:
        """ Get all lesson plans """
        plan_list =  self._db.list_all(f"{group_id}/plans")
        plan_list = [plan[:-5] for plan in plan_list]
        return plan_list

    def update_plan(self, name: str, group_id: int, new_plan: Plan, new_name: str = "") -> bool:
        """ Update a lesson plan """
        if new_name:
            self._db.delete(f"{group_id}/plans", name)
            return self._db.save(new_plan, f"{group_id}/plans", new_name)
        return self._db.save(new_plan, f"{group_id}/plans", name)

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
                    time_diff = f"{int(diff // 3600)}h {int((diff % 3600) // 60):02}min"
                for student in plan.students:
                    free_students.append((student, time_diff))
        return free_students
