""" Class for Plan """

from .lesson import Lesson

class Plan:
    """ Plan class containing info about lessons """
    def __init__(self, name: str) -> None:
        self._name = name
        self._students = []
        self._week = [[] for _ in range(5)]
        self._days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    @property
    def monday(self) -> list:
        """ Returns the lessons for Monday """
        return self._week[0]

    @property
    def tuesday(self) -> list:
        """ Returns the lessons for Tuesday """
        return self._week[1]

    @property
    def wednesday(self) -> list:
        """ Returns the lessons for Wednesday """
        return self._week[2]

    @property
    def thursday(self) -> list:
        """ Returns the lessons for Thursday """
        return self._week[3]

    @property
    def friday(self) -> list:
        """ Returns the lessons for Friday """
        return self._week[4]

    def add_student(self, student_id: int) -> None:
        """ Add a student to the plan """
        self._students.append(student_id)

    def remove_student(self, student_id: int) -> None:
        """ Remove a student from the plan """
        self._students.remove(student_id)

    def add_lesson(self, day: int, lesson: Lesson) -> None:
        """ Add a lesson to the plan """
        self._week[day].append(lesson)

    def remove_lesson(self, day: int, lesson: Lesson) -> None:
        """ Remove a lesson from the plan """
        self._week[day].remove(lesson)

    def clear_day(self, day: int) -> None:
        """ Clear all lessons for a day """
        self._week[day].clear()

    def clear_all(self) -> None:
        """ Clear all lessons """
        for day in self._week:
            day.clear()

    def get_day(self, day: int) -> list:
        """ Get all lessons for a day """
        return self._week[day]

    def get_all(self) -> list:
        """ Get all lessons """
        return self._week

    def __str__(self) -> str:
        plan = ""
        for i, day in enumerate(self._week):
            plan += f"{self._days[i]}:\n"
            plan += "\n".join(day) + "\n"
        return plan
