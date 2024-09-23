""" Class for Plan """

from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
from .lesson import Lesson

class Plan:
    """ Plan class containing info about lessons """
    _days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    def __init__(self, name: str) -> None:
        self._name = name
        self._students = []
        self._week: list[list[Lesson]] = [[] for _ in range(5)]

    @property
    def students(self) -> list:
        """ Returns the students of the plan """
        return self._students

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

    @property
    def next_lesson(self) -> Lesson | None:
        """ Returns the next lesson """
        today = datetime.now().weekday()
        now = datetime.now().time()
        for lesson in self._week[today]:
            if lesson.start_time > now:
                return lesson
        return None

    def add_student(self, student_id: int) -> None:
        """ Add a student to the plan """
        self._students.append(student_id)

    def remove_student(self, student_id: int) -> None:
        """ Remove a student from the plan """
        self._students.remove(student_id)

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

    def to_image(self) -> bytes:
        """ Create an image of the plan """
        if self.is_empty():
            return b""

        max_lessons = max([len(day) for day in self._week])

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#222222')
        ax.set_facecolor('#222222')

        col_labels = self._days
        table_data = []

        for i in range(max_lessons):
            row = []
            for day in self._week:
                if i < len(day):
                    row.append(str(day[i]))
                else:
                    row.append("")
            table_data.append(row)

        row_labels = [f"Lesson {i+1}" for i in range(max_lessons)]

        ax.axis("tight")
        ax.axis("off")

        table = ax.table(cellText=table_data, rowLabels=row_labels,
                        colLabels=col_labels, loc="center", cellLoc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(7)
        table.scale(1, 3)

        for cell in table.get_celld().values():
            cell.set_edgecolor('#222222')
            cell.set_facecolor('darkgrey')

        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        with open("plan.png", "wb") as file:
            file.write(buf.read())
        return buf.getvalue()
