from .lesson import Lesson
from .day import Day
from telebot.types import User

class Plan():
    def __init__(self) -> None:
        self.days = [Day() for _ in range(7)]
        self.people = {}
    
    def add_lesson(self, day: int, lesson: Lesson) -> None:
        """ adds a lesson to the specified weekday

        Args:
            day (int): day of the week (0-6)
            lesson (Lesson): lesson to add

        Raises:
            ValueError: if day is out of bounds
            
        """
        if day not in range(7):
            raise ValueError("Day out of bounds.")

        self.days[day].add_lesson(lesson)
    
    def remove_lesson(self, day: int, idx: int) -> None:
        """ removes a lesson from the specified weekday at the specified index

        Args:
            day (int): day of the week (0-6)
            idx (int): index of the lesson to remove

        Raises:
            IndexError: if idx is out of bounds
            ValueError: if day is out of bounds

        """
        if day not in range(7):
            raise ValueError("Day out of bounds.")

        self.days[day].remove_lesson(idx)

    def get_lessons(self, day: int) -> list[Lesson]:
        """ returns the list of lessons for the specified day

        Args:
            day (int): day of the week (0-6)

        Returns:
            list[Lesson]: list of lessons for the specified day

        Raises:
            ValueError: if day is out of bounds

        """
        if day not in range(7):
            raise ValueError("Day out of bounds.")
        
        return self.days[day].get_lessons()
    
    def get_lesson(self, day: int, idx: int) -> Lesson:
        """ returns the lesson at the specified index for the specified day

        Args:
            day (int): day of the week (0-6)
            idx (int): index of the lesson to return

        Returns:
            Lesson: lesson at the specified index for the specified day

        Raises:
            IndexError: if idx is out of bounds
            ValueError: if day is out of bounds

        """
        if day not in range(7):
            raise ValueError("Day out of bounds.")

        return self.days[day].get_lesson(idx)
    
    def add_person(self, person: User) -> None:
        """ adds a person to the plan with the specified id (optional)

        Args:
            person (telebot.types.User): person to add
            
        """
        person_id = person.id

        self.people[person_id] = person
    
    def remove_person(self, person_id: int) -> None:
        """ removes a person from the plan

        Args:
            person_id (int): id of the person to remove

        Raises:
            KeyError: if person_id is not in the plan
        
        """
        del self.people[person_id]
    
    def __str__(self) -> str:
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        result = ""
        for i, day in enumerate(self.days):
            result += f"{day_names[i]}:\n"
            for lesson in day.get_lessons():
                result += str(lesson)
        return result
    
    def retarded_str(self) -> str:
        result = ""
        for i, day in enumerate(self.days):
            result += f"Day {i + 1}:\n"
            for lesson in day.get_lessons():
                result += str(lesson)
        return result