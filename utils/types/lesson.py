from __future__ import annotations
import datetime

from enum import Enum

class LessonType(Enum):
    LECTURE = "lecture"
    SEMINAR = "seminar"
    LAB = "lab"
    EXERCISE = "exercise"
    PROJECT = "project"
    CONSULTATION = "consultation"
    EXAM = "exam"
    OTHER = "other"
    
    def from_str(string: str) -> LessonType:
        """ returns LessonType from string

        Args:
            string (str): string to convert

        Returns:
            LessonType: LessonType from string, LessonType.OTHER if not found

        """
        lowered_string = str.lower(string)
        for type_of_lesson in LessonType:
            if type_of_lesson.value == lowered_string:
                return type_of_lesson
        
        return LessonType.OTHER

class Lesson():
    def __init__(self, arguments: dict[str, str] | None = None) -> None:
        self._subject = "--"
        self._room = "--"
        self._type = LessonType.OTHER
        self._start = datetime.time(0, 0)
        self._end = datetime.time(0, 0)

        if arguments:
            self.read_args(arguments)
    
    def read_args(self, arguments: dict[str, str]) -> None:
        """ will read all new values from arguments and update the lesson, won't update if the argument is invalid

        Args:
            arguments (dict[str, str]): dictionary with the new values

        """
        self._subject = arguments.get("subject", self._subject)
        self._room = arguments.get("room", self._room)
        self._type = LessonType.from_str(arguments.get("type", self._type.value))
        try:
            self._start = datetime.datetime.strptime(arguments.get("start", ":"), "%H:%M").time()
        except ValueError:
            pass
        try:  
            self._end = datetime.datetime.strptime(arguments.get("end", ":"), "%H:%M").time()
        except ValueError:
            pass

    def is_now(self) -> bool:
        return self._start <= datetime.datetime.now().time() <= self._end
        
    def __str__(self) -> str:
        start_time = self._start.strftime("%H:%M")
        end_time = self._end.strftime("%H:%M")
        return f"{self._subject} | {self._room} | {start_time} | {end_time} ({self._type})\n"
    
    def __lt__(self, other: Lesson) -> bool:
        return self._start < other._start