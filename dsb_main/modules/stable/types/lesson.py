""" Class for Lesson """

from datetime import datetime, time, date, timedelta

class Lesson:
    """ Lesson class containing info about a lesson """
    def __init__(self, subject: str, teacher: str, room: str, # pylint: disable=too-many-arguments
                 start_time: time, end_time: time, day: int, lesson_type: str) -> None:
        self._subject = subject
        self._teacher = teacher
        self._day = day
        self._room = room
        self._start_time = start_time
        self._end_time = end_time
        self._duration = datetime.combine(date.today(), self._end_time) - \
            datetime.combine(date.today(), self._start_time)
        self._type = lesson_type

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
    def duration(self) -> time:
        """ Returns the duration of the lesson """
        return self._duration

    @property
    def day(self) -> int:
        """ Returns the day of the lesson """
        return self._day

    @property
    def is_now(self) -> bool:
        """ Returns True if the lesson is now """
        today = datetime.now().weekday()
        if today != self._day:
            return False
        now = datetime.now().time()
        return self._start_time <= now <= self._end_time

    @property
    def time_left(self) -> time:
        """ Returns the time left for the lesson """
        if not self.is_now:
            return time(0, 0)
        now = datetime.now().time()
        return self._end_time - now

    @property
    def time_until(self) -> timedelta:
        """ Returns the time until the lesson """
        if self.is_now or datetime.now().time() > self._start_time:
            return time(0, 0)
        now = datetime.now()
        return datetime.combine(date.today(), self._start_time) - now

    def update(self, data: dict):
        """ Update the lesson with new data """
        self._subject = data.get("subject", self._subject)
        self._teacher = data.get("teacher", self._teacher)
        self._room = data.get("room", self._room)
        if "start_time" in data:
            self._start_time = datetime.strptime(data["start_time"], "%H:%M").time()
        if "end_time" in data:
            self._end_time = datetime.strptime(data["end_time"], "%H:%M").time()
        self._duration = self._end_time - self._start_time
        self._type = data.get("type", self._type)

    def __str__(self) -> str:
        s_time = datetime.combine(date.today(), self._start_time)
        e_time = datetime.combine(date.today(), self._end_time)
        s_display = datetime.strftime(s_time, "%H:%M")
        e_display = datetime.strftime(e_time, "%H:%M")
        return f"{self.subject} | {self._type}" + \
            f" | {self._teacher} | {self._room} | {s_display} - {e_display}"
