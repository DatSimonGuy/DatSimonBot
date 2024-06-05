import os
import jsonpickle
from .plan import Plan
from .lesson import Lesson
from telebot.types import User

class Database():
    def __init__(self, path: str) -> None:
        self.path = path
        self.plans: dict[int, dict[str, Plan]] = {}
        os.makedirs(self.path, exist_ok=True)
    
    def new_plan(self, group_id: int, plan_name: str) -> None:
        """ creates a new plan with the specified name for the specified group id

        Args:
            group_id (int): group id
            plan_name (str): name of the new plan

        Raises:
            ValueError: if plan already exists

        """
        if plan_name in self.plans[group_id]:
            raise ValueError("Plan already exists.")

        try:
            self.plans[group_id][plan_name] = Plan()
            self.save()
        except KeyError:
            self.plans[group_id] = {plan_name: Plan()}
        
    
    def remove_plan(self, group_id: int, plan_name: str) -> None:
        """ removes a plan with the specified name for the specified group id

        Args:
            group_id (int): group id
            plan_name (str): name of the plan to remove

        Raises:
            ValueError: if plan does not exist

        """
        try:
            del self.plans[group_id][plan_name]
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
            return self.plans[group_id][plan_name]
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
            self.plans[group_id][plan_name].add_person(person)
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
            self.plans[group_id][plan_name].remove_person(person_id)
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
            self.plans[group_id][plan_name].add_lesson(day, lesson)
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
            self.plans[group_id][plan_name].remove_lesson(day, idx)
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
            return self.plans[group_id][plan_name].get_lesson(day, idx)
        except ValueError or IndexError:
            raise ValueError(f"Lesson {idx} does not exist in the plan {plan_name} for group {group_id}.")
    
    def save(self) -> None:
        """ saves the database to a file located at self.path/database.json
        """
        with open(self.path + "/database.json", "w") as f:
            f.write(jsonpickle.encode(self.plans, indent=1, keys=True))
    
    def load(self) -> None:
        """ loads the database from a file located at self.path/database.json if it exists
        """
        try:
            with open(self.path + "/database.json", "r") as f:
                self.plans = jsonpickle.decode(f.read(), keys=True)
        except FileNotFoundError:
            return