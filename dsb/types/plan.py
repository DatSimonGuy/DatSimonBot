""" Class for Plan """

from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
from dsb.types.errors import DSBError
from .lesson import Lesson

class AlreadyInPlanError(DSBError):
    """ Raised when the student is already in the plan """
    def __init__(self) -> None:
        super().__init__("You are already in the plan")

class NotInPlanError(DSBError):
    """ Raised when the student is not in the plan """
    def __init__(self) -> None:
        super().__init__("You are not in the plan")

class Plan:
    """ Plan class containing info about lessons """
    _days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    def __init__(self, owner: int | None = None) -> None:
        self._students = []
        self._week: list[list[Lesson]] = [[] for _ in range(5)]
        self._owner: int | None = owner

    @property
    def owner(self) -> int | None:
        """ Returns the owner of the plan """
        return self._owner

    @owner.setter
    def owner(self, owner: int) -> None:
        """ Set the owner of the plan """
        self._owner = owner

    @property
    def students(self) -> list:
        """ Returns the students of the plan """
        return self._students

    @property
    def next_lesson(self) -> Lesson | None:
        """ Returns the next lesson """
        today = datetime.now().weekday()
        now = datetime.now().time()
        for lesson in self._week[today]:
            if not lesson.active:
                continue
            if lesson.start_time > now:
                return lesson
        return None

    @property
    def current_lesson(self) -> Lesson | None:
        """ Returns the current lesson """
        today = datetime.now().weekday()
        now = datetime.now().time()
        for lesson in self._week[today]:
            if not lesson.active:
                continue
            if lesson.start_time <= now <= lesson.end_time:
                return lesson
        return None

    def is_free(self) -> bool:
        """ Returns True if the students are free """
        if self.current_lesson:
            return False
        return True

    def add_student(self, username: str) -> None:
        """ Add a student to the plan """
        if username not in self._students:
            self._students.append(username)
        else:
            raise AlreadyInPlanError()

    def remove_student(self, student_id: int) -> None:
        """ Remove a student from the plan """
        try:
            self._students.remove(student_id)
        except ValueError as exc:
            raise NotInPlanError() from exc

    def add_lesson(self, day: int, lesson: Lesson) -> None:
        """ Add a lesson to the plan """
        self._week[day].append(lesson)
        self._week[day].sort(key=lambda x: x.start_time)

    def remove_lesson(self, day: int, lesson: Lesson) -> None:
        """ Remove a lesson from the plan """
        self._week[day].remove(lesson)

    def remove_lesson_by_index(self, day: int, index: int) -> None:
        """ Remove a lesson from the plan by index """
        self._week[day].pop(index)

    def clear_day(self, day: int) -> None:
        """ Clear all lessons for a day """
        self._week[day].clear()

    def clear_all(self) -> None:
        """ Clear all lessons """
        for day in self._week:
            day.clear()

    def get_day(self, day: int) -> list[Lesson]:
        """ Get all lessons for a day """
        return self._week[day]

    def get_all(self) -> list:
        """ Get all lessons """
        return self._week

    def is_empty(self) -> bool:
        """ Returns True if the plan is empty """
        for day in self._week:
            if day:
                return False
        return True

    def __str__(self) -> str:
        plan = ""
        for i, day in enumerate(self._week):
            plan += f"{self._days[i]}:\n"
            for lesson in day:
                plan += f"{str(lesson)}\n"
        return plan

    def to_image(self, title: str = "Plan") -> bytes:
        """ Create an image of the plan """
        if self.is_empty():
            return b""

        colors_by_type = {
            "lecture": "#5b9fe6",
            "exercise": "#f1559e",
            "test": "#f7b731",
            "exam": "#f7b731",
            "lab": "#9f7dde",
            "project": "#ee9e57",
            "seminar": "#90ee90",
            "lektorat": "#11c5ae",
            "other": "#808080"
        }

        matplotlib.use('Agg')
        fig, ax = plt.subplots()
        ax.set_title(title, fontsize=16, color="black")
        fig.legend(handles=[plt.Rectangle((0, 0), 1, 1,
                                          color=color) for color in colors_by_type.values()],
                   labels=colors_by_type.keys(), loc="upper right", fontsize=6)
        ax.axis("tight")

        for i in range(6):
            ax.plot([i, i], [0, 14], color="black")

        for i in range(7, 21):
            ax.plot([0, 5], [i-7, i-7], color="black")

        for i, day in enumerate(self._week):
            for lesson in day:
                start = lesson.start_time
                end = lesson.end_time
                color = colors_by_type.get(lesson.type, "#808080")
                if not lesson.active:
                    color = matplotlib.colors.to_rgba(color, alpha=0.3)
                ax.fill_between([i+0.01, i + 0.99], [start.hour - 7 + start.minute / 60],
                                [end.hour - 7 + end.minute / 60],
                                color=color, zorder=2,
                                edgecolor="black", linewidth=0.5)
                start_d = lesson.start_time.strftime("%H:%M")
                end_d = lesson.end_time.strftime("%H:%M")
                lesson_text = f"{lesson.subject}\n{lesson.room}\n{start_d}-{end_d}"
                text_y = min(start.hour - 7 + start.minute / 60 + 0.5 + 0.4, 13.5)
                ax.text(i + 0.5, text_y, lesson_text, color="black",
                        fontdict={"fontsize": 5, "ha": "center", "va": "bottom"},
                        zorder=3)

        ax.set_xlim(0, 5)
        ax.set_ylim(14, 0)
        ax.set_yticks(range(14))
        ax.set_yticklabels([f"{i+7}:00" for i in range(14)], fontsize=8, color="black")

        ax.set_xticks([0.5, 1.5, 2.5, 3.5, 4.5])
        ax.set_xticklabels(self._days, fontsize=10, color="black", ha='center')
        ax.xaxis.set_label_position('top')
        ax.xaxis.tick_top()

        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=600)
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()
