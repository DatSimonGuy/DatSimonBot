from __future__ import annotations
import datetime
import os
import jsonpickle
from telebot.types import User

class PersonType():
    STUDENT = "Student"
    ADMIN = "Admin"

class LessonType():
    LECTURE = "Lecture"
    SEMINAR = "Seminar"
    LAB = "Lab"
    EXERCISE = "Exercise"
    PROJECT = "Project"
    CONSULTATION = "Consultation"
    EXAM = "Exam"
    OTHER = "Other"
    
    def str_to_type(string: str) -> LessonType:
        match(string.lower()):
            case "lecture":
                return LessonType.LECTURE
            case "seminar":
                return LessonType.SEMINAR
            case "lab":
                return LessonType.LAB
            case "exercise":
                return LessonType.EXERCISE
            case "project":
                return LessonType.PROJECT
            case "consultation":
                return LessonType.CONSULTATION
            case "exam":
                return LessonType.EXAM
            case "other":
                return LessonType.OTHER
            case _:
                raise ValueError("Invalid lesson type.")

class Lesson():
    def __init__(self) -> None:
        self.subject = "--"
        self.room = "--"
        self.type = LessonType.OTHER
        self.start = datetime.time(0, 0)
        self.end = datetime.time(0, 0)
    
    def __str__(self) -> str:
        start_time = self.start.strftime("%H:%M")
        end_time = self.end.strftime("%H:%M")
        return f"{self.subject} | {self.room} | {start_time} | {end_time} ({self.type})\n"
    
    def __lt__(self, other: Lesson) -> bool:
        return self.start < other.start

class Day():
    def __init__(self) -> None:
        self.lessons = []
    
    def add_lesson(self, lesson: Lesson) -> None:
        self.lessons.append(lesson)
    
    def remove_lesson(self, lesson: Lesson) -> None:
        self.lessons.remove(lesson)

class Plan():
    def __init__(self) -> None:
        self.days = [Day() for _ in range(7)]
        self.people = {}
    
    def add_lesson(self, day: int, lesson: Lesson) -> None:
        self.days[day].add_lesson(lesson)
    
    def remove_lesson(self, day: int, lesson: Lesson) -> None:
        self.days[day].remove_lesson(lesson)

    def get_lessons(self, day: int) -> list[Lesson]:
        return self.days[day].lessons
    
    def add_person(self, person_id: int, person: User) -> None:
        self.people[person_id] = person
    
    def remove_person(self, person_id: int) -> None:
        del self.people[person_id]

class Database():
    def __init__(self, path: str) -> None:
        self.path = path
        self.plans: dict[int, dict[str, Plan]] = {}
        os.makedirs(self.path, exist_ok=True)
    
    def new_plan(self, group_id: int, plan_name: str) -> None:
        if plan_name in self.plans:
            raise ValueError("Plan already exists.")
        try:
            self.plans[group_id][plan_name] = Plan()
        except KeyError:
            self.plans[group_id] = {plan_name: Plan()}
    
    def remove_plan(self, group_id: int, plan_name: str) -> None:
        try:
            del self.plans[group_id][plan_name]
        except KeyError:
            raise ValueError("Plan does not exist.")
    
    def get_plan(self, group_id: int, plan_name: str) -> Plan:
        return self.plans[group_id][plan_name]

    def add_person(self, group_id: int, plan_name: str, person_id: int, person: User) -> None:
        self.plans[group_id][plan_name].add_person(person_id, person)
    
    def remove_person(self, group_id: int, plan_name: str, person_id: int) -> None:
        self.plans[group_id][plan_name].remove_person(person_id)
    
    def add_lesson(self, group_id: int, plan_name: str, day: int, lesson: Lesson) -> None:
        self.plans[group_id][plan_name].add_lesson(day, lesson)
        self.plans[group_id][plan_name].days[day].lessons.sort()
    
    def remove_lesson(self, group_id: int, plan_name: str, day: int, lesson: Lesson) -> None:
        self.plans[group_id][plan_name].remove_lesson(day, lesson)
    
    def save(self) -> None:
        with open(self.path + "/database.json", "w") as f:
            f.write(jsonpickle.encode(self.plans, indent=1, keys=True))
    
    def load(self) -> None:
        try:
            with open(self.path + "/database.json", "r") as f:
                self.plans = jsonpickle.decode(f.read(), keys=True)
        except FileNotFoundError:
            return