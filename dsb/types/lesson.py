""" Class for Lesson """

from datetime import datetime, time, date, timedelta
from dsb.utils.transforms import str_to_day, str_to_time
from dsb.types.errors import InvalidValueError, DSBError

class NameTooLongError(DSBError):
    """ Raised when the name of the lesson is too long """
    def __init__(self) -> None:
        super().__init__("Subject name cannot be more than 20 characters long")

class Lesson:
    """ Lesson class containing info about a lesson """
    def __init__(self, lesson_data: dict[str, str]) -> None:
        try:
            day = lesson_data["day"]
            start = lesson_data["start"]
            end = lesson_data["end"]
            subject = lesson_data["subject"]
            day = str_to_day(day)
            if not day:
                raise InvalidValueError("day")
            start = str_to_time(start)
            end = str_to_time(end)
            if not all((start, end)):
                raise InvalidValueError("time")
            if len(subject) >= 20:
                raise NameTooLongError()
            self._subject = subject
            self._start_time = start
            self._end_time = end
            self._day = day
            self._type = lesson_data["type"]
            self._room = lesson_data["room"]
            self._teacher = lesson_data["teacher"]
            self._repeat = lesson_data.get("repeat", "not")
            if self._repeat not in ["not", "even", "odd"]:
                raise InvalidValueError("repeat")
        except KeyError as key:
            raise InvalidValueError(key) from key

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

    @property
    def active(self) -> bool:
        """ Returns True if the lesson is active """
        if not hasattr(self, "_repeat"):
            self._repeat = "not"
        if self._repeat == "not":
            return True
        today = datetime.now().isocalendar()[1]
        if self._repeat == "even":
            return today % 2 == 0
        return today % 2 != 0

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
