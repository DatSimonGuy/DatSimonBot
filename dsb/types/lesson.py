""" Class for Lesson """

from typing import Optional
from datetime import datetime, time, date, timedelta

def get_valid_day(string: str) -> Optional[int]:
    """ Convert string to a valid day value """
    if string.isdigit():
        day = int(string)
        if day not in range(1, 5):
            return None
        return day
    days = {
        "monday": 1,
        "tuesday": 2,
        "wednesday": 3,
        "thursday": 4,
        "friday": 5
    }
    day = days.get(string.lower(), None)
    return day

def get_valid_time(string: str) -> time:
    """ Get valid datetime.time from string """
    try:
        return datetime.strptime(string, "%H:%M").time()
    except Exception: #pylint: disable=broad-exception-caught
        return None

class Lesson:
    """ Lesson class containing info about a lesson """
    def __init__(self, lesson_data: dict[str, str], repeat: bool = False) -> None:
        day = lesson_data["day"]
        start = lesson_data["start"]
        end = lesson_data["end"]
        subject = lesson_data["subject"]
        day = get_valid_day(day)
        if not day:
            raise ValueError("Invalid day")
        start = get_valid_time(start)
        end = get_valid_time(end)
        if not all((start, end)):
            raise ValueError("Invalid start time / end time")
        if len(subject) >= 20:
            raise ValueError("Subject name cannot be more than 20 characters long")
        self._subject = subject
        self._start_time = start
        self._end_time = end
        self._day = day
        self._type = lesson_data["type"]
        self._room = lesson_data["room"]
        self._teacher = lesson_data["teacher"]
        self._repeat = repeat

    @property
    def subject(self) -> str:
        """ Returns the name of the lesson """
        return self._subject

    @property
    def teacher(self) -> str:
        """ Returns the teacher of the lesson """
        return self._teacher

    @property
    def room(self) -> str:
        """ Returns the room of the lesson """
        return self._room

    @property
    def start_time(self) -> time:
        """ Returns the start time of the lesson """
        return self._start_time

    @property
    def end_time(self) -> time:
        """ Returns the end time of the lesson """
        return self._end_time

    @property
    def day(self) -> int:
        """ Returns the day of the lesson """
        return self._day

    @property
    def is_now(self) -> bool:
        """ Returns True if the lesson is now """
        today = datetime.now().weekday() + 1
        if today != int(self._day):
            return False
        now = datetime.now().time()
        return self._start_time <= now <= self._end_time

    @property
    def time_left(self) -> timedelta:
        """ Returns the time left for the lesson """
        if not self.is_now:
            return timedelta(0, 0, 0)
        now = datetime.now()
        return datetime.combine(date.today(), self._end_time) - now

    @property
    def time_until(self) -> timedelta:
        """ Returns the time until the lesson """
        if self.is_now or datetime.now().time() > self._start_time:
            return timedelta(0, 0, 0)
        now = datetime.now()
        return datetime.combine(date.today(), self._start_time) - now

    @property
    def type(self) -> str:
        """ Returns the type of the lesson """
        return self._type

    def to_dict(self) -> dict[str, str]:
        """ Returns the lesson as a dictionary """
        return {
            "subject": self._subject,
            "teacher": self._teacher,
            "room": self._room,
            "start": self._start_time.strftime("%H:%M"),
            "end": self._end_time.strftime("%H:%M"),
            "day": self._day,
            "type": self._type,
            "repeat": self._repeat if hasattr(self, "_repeat") else False
        }

    def __str__(self) -> str:
        s_time = datetime.combine(date.today(), self._start_time)
        e_time = datetime.combine(date.today(), self._end_time)
        s_display = datetime.strftime(s_time, "%H:%M")
        e_display = datetime.strftime(e_time, "%H:%M")
        return f"| {s_display} - {e_display} | {self.subject} | {self._type} |\n" + \
            f" | {self._teacher} | {self._room} | "
