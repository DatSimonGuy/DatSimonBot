from ..plan import Plan
from ..lesson import Lesson
from telebot.types import User
from .database import Database

class PlansDatabase(Database):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._data: dict[int, dict[str, Plan]] = {}
    
    def new_plan(self, group_id: int, plan_name: str) -> None:
        """ creates a new plan with the specified name for the specified group id

        Args:
            group_id (int): group id
            plan_name (str): name of the new plan

        Raises:
            ValueError: if plan already exists

        """

        try:
            if plan_name in self._data[group_id]:
                raise ValueError("Plan already exists.")
            self._data[group_id][plan_name] = Plan()
        except KeyError:
            self._data[group_id] = {plan_name: Plan()}
        
        self.save()
    
    def remove_plan(self, group_id: int, plan_name: str) -> None:
        """ removes a plan with the specified name for the specified group id

        Args:
            group_id (int): group id
            plan_name (str): name of the plan to remove

        Raises:
            ValueError: if plan does not exist

        """
        try:
            del self._data[group_id][plan_name]
            self.save()
        except KeyError:
            raise ValueError(f"Plan {plan_name} does not exist.")

    def get_plan(self, group_id: int, plan_name: str) -> Plan:
        """ returns the plan with the specified name for the specified group id

        Args:
            group_id (int): group id
            plan_name (str): name of the plan to return

        Returns:
            Plan: plan with the specified name

        Raises:
            ValueError: if plan does not exist

        """
        try:
            return self._data[group_id][plan_name]
        except KeyError:
            raise ValueError(f"Plan {plan_name} does not exist.")

    def add_person(self, group_id: int, plan_name: str, person: User) -> None:
        """ adds a person to the plan

        Args:
            group_id (int): group id
            plan_name (str): name of the plan
            person (User): person to add

        Raises:
            ValueError: if plan does not exist

        """
        try:
            self._data[group_id][plan_name].add_person(person)
            self.save()
        except:
            raise ValueError(f"Plan {plan_name} does not exist for group {group_id}.")

    def remove_person(self, group_id: int, plan_name: str, person_id: int) -> None:
        """ removes a person from the plan

        Args:
            group_id (int): group id
            plan_name (str): name of the plan
            person_id (int): id of the person to remove

        Raises:
            ValueError: if person is not in the plan for the specified group

        """
        try:
            self._data[group_id][plan_name].remove_person(person_id)
            self.save()
        except KeyError:
            raise ValueError(f"Person {person_id} is not in the plan {plan_name} for group {group_id}.")
    
    def add_lesson(self, group_id: int, plan_name: str, day: int, lesson: Lesson) -> None:
        """ adds a lesson to the plan

        Args:
            group_id (int): group id
            plan_name (str): name of the plan
            day (int): day of the week (0-6)
            lesson (Lesson): lesson to add

        Raises:
            ValueError: if plan does not exist
            ValueError: if day is out of bounds

        """
        try:
            self._data[group_id][plan_name].add_lesson(day, lesson)
            self.save()
        except KeyError:
            raise ValueError(f"Plan {plan_name} does not exist for group {group_id}.")

    def remove_lesson(self, group_id: int, plan_name: str, day: int, idx: int) -> None:
        """ removes a lesson from the plan

        Args:
            group_id (int): group id
            plan_name (str): name of the plan
            day (int): day of the week (0-6)
            idx (int): index of the lesson to remove

        Raises:
            ValueError: if plan does not exist
            ValueError: if day is out of bounds

        """
        try:
            self._data[group_id][plan_name].remove_lesson(day, idx)
            self.save()
        except KeyError or IndexError:
            raise ValueError(f"Plan {plan_name} does not exist for group {group_id}.")
    
    def get_lesson(self, group_id: int, plan_name: str, day: int, idx: int) -> Lesson:
        """ returns a lesson from the plan

        Args:
            group_id (int): group id
            plan_name (str): name of the plan
            day (int): day of the week (0-6)
            idx (int): index of the lesson to return

        Returns:
            Lesson: lesson from the plan

        Raises:
            ValueError: if plan does not exist
            ValueError: if day is out of bounds
            ValueError: if lesson does not exist
        
        """
        try:
            return self._data[group_id][plan_name].get_lesson(day, idx)
        except ValueError or IndexError:
            raise ValueError(f"Lesson {idx} does not exist in the plan {plan_name} for group {group_id}.")