import time
from telebot.types import InlineKeyboardMarkup
from utils.fileHandler import SaveData, Delete, ReadData
from utils.converter import ToDate, ToTime, PageArrows, ToKeyboard
from datetime import datetime, date, time

class Person:
    """
    Represents a person with a name, last name, nickname, ID, and birthdate.

    Attributes:
        name (str): The person's first name.
        last_name (str): The person's last name.
        nick (str): The person's nickname.
        id (int): The person's ID.
        birthdate (date, optional): The person's birthdate. Defaults to None.
    """

    def __init__(self, name: str, last_name: str, nick: str, id: int, birthdate: date = None, role: list = []):
        self.name = name
        self.last_name = last_name
        self.birthdate = birthdate
        self.id = id
        self.nick = nick
        self.role = role

    def __str__(self) -> str:
        return f"{self.nick}"

class Student(Person):
    """
    Represents a student.

    Attributes:
        name (str): The student's first name.
        last_name (str): The student's last name.
        nick (str): The student's nickname.
        id (int): The student's ID number.
        major (str): The student's major.
        group (str): The student's group.
        index (int, optional): The student's index number. Defaults to 0.
        birthdate (date, optional): The student's birthdate. Defaults to None.
    """

    def __init__(self, name: str, last_name: str, nick: str, id: int, major: str, group: str, index: int = 0, birthdate: date = None, roles: list = ["student"]):
        if "student" not in roles:
            roles.append("student")
        super().__init__(name, last_name, nick, id, birthdate, roles)
        self.major = major
        self.group = group
        self.index = index
        
def CreateStudentFromUser(user, major: str, group: str, index: int):
    """
    Creates a Student object from a User object.

    Args:
        user (User): The User object containing the user's information.
        major (str): The major of the student.
        group (str): The group of the student.
        index (int): The index of the student.

    Returns:
        Student: A Student object created from the user's information.
    """
    nick = user.username
    name = user.first_name
    last_name = user.last_name
    id = user.id
    return Student(name, last_name, nick, id, major, group, index)

def CreatePersonFromUser(user):
    """
    Create a Person object from a User object.

    Args:
        user (User): The User object containing the user's information.

    Returns:
        Person: A Person object created from the user's information.
    """
    nick = user.username
    name = user.first_name
    last_name = user.last_name
    id = user.id
    return Person(name, last_name, nick, id)
        

from datetime import time

class Lesson:
    """
    Represents a lesson with its attributes.

    Attributes:
        beginning (time): The starting time of the lesson.
        ending (time): The ending time of the lesson.
        subject (str): The subject of the lesson.
        type (str): The type of the lesson.
        classroom (str): The classroom where the lesson takes place.
        repeat_in (int, optional): The number of times the lesson repeats. Defaults to 1.
        active (bool, optional): Indicates if the lesson is active. Defaults to True.
        once_in_weeks (int, optional): The number of weeks between each occurrence of the lesson. Defaults to 1.
    """

    def __init__(self, beginning: time, ending: time, subject: str, type: str, classroom: str, repeat_in: int = 1, active: bool = True, once_in_weeks: int = 1):
        if isinstance(beginning, str):
            self.beginning = ToTime(beginning)
        else:
            self.beginning = beginning
        if isinstance(ending, str):
            self.ending = ToTime(ending)
        else:
            self.ending = ending
        self.subject = subject
        self.type = type
        self.classroom = classroom
        self.repeat_in = repeat_in
        self.once_in_weeks = once_in_weeks
        self.active = active
    
    def __str__(self):
        return f'{self.subject} | {self.type} | {str(self.beginning)[:5]} | {str(self.ending)[:5]} | {self.classroom}\n'


class Day:
    """
    Represents a day of the week with a list of lessons.

    Attributes:
        weekday (str): The name of the weekday.
        lessons (list): A list of Lesson objects representing the lessons for the day.
    """

    def __init__(self, weekday: str, lessons: list = []):
        """
        Initializes a Day object.

        Args:
            weekday (str): The name of the weekday.
            lessons (list, optional): A list of Lesson objects representing the lessons for the day. Defaults to an empty list.
        """
        self.lessons = lessons
        self.weekday = weekday
    
    def __str__(self):
        """
        Returns a string representation of the Day object.

        Returns:
            str: A string representation of the Day object.
        """
        day = f'{self.weekday}:\n'
        for i, lesson in enumerate(self.lessons):
            day += f'{i}. {str(lesson)}\n'
        return day if len(self.lessons) > 0 else f'{self.weekday}:\nFree\n\n'
    
    def addLesson(self, new_lesson: Lesson):
        """
        Adds a new lesson to the Day object.

        Args:
            new_lesson (Lesson): The Lesson object to be added.
        """
        for i, lesson in enumerate(reversed(self.lessons)):
            if lesson.beginning < new_lesson.beginning:
                self.lessons.insert(len(self.lessons) + 1 - i, new_lesson)
                return
        self.lessons.insert(0, new_lesson)
        
    def removeLesson(self, idx: int):
        """
        Removes a lesson from the Day object.

        Args:
            idx (int): The index of the lesson to be removed.
        """
        self.lessons.pop(idx)
    
    def editLesson(self, idx: int, type: str, value):
        """
        Edits a lesson in the Day object.

        Args:
            idx (int): The index of the lesson to be edited.
            type (str): The type of the lesson attribute to be edited.
            value: The new value of the lesson attribute.
        """
        lesson = self.lessons[idx]
        if type == "beginning":
            lesson.beginning = ToTime(value)
        elif type == "ending":
            lesson.ending = ToTime(value)
        elif type == "subject":
            lesson.subject = value
        elif type == "type":
            lesson.type = value
        elif type == "classroom":
            lesson.classroom = value
        elif type == "repeat_in":
            lesson.repeat_in = int(value)
        elif type == "once_in_weeks":
            lesson.once_in_weeks = int(value)
        elif type == "active":
            lesson.active = value
    
    def status(self):
        """
        Returns the status of the Day object (busy, break, or free).

        Returns:
            str: The status of the Day object.
        """
        now = datetime.now().time()
        for lesson in self.lessons:
            if not lesson.active:
                continue
            if lesson.beginning < now and lesson.ending > now:
                return "Busy"
            elif lesson.beginning > now:
                return "Break"
        return "Free"

class Plan:
    """
    Represents a weekly plan consisting of weekdays and their associated lessons.
    """

    def __init__(self, weekdays : list[Day] = []):
        """
        Initializes a Plan object.

        Parameters:
        - weekdays (list[Day]): A list of Day objects representing the weekdays of the plan.
        """
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days_of_week:
            weekdays.append(Day(day))
        self.weekdays = weekdays
    
    def __str__(self):
        """
        Returns a string representation of the plan.

        Returns:
        - str: A string representation of the plan.
        """
        week = ""
        for day in self.weekdays:
            week += f'{str(day)}'
        return week
    
    def addLesson(self, weekday : int, lesson : Lesson):
        """
        Adds a lesson to a specific weekday in the plan.

        Parameters:
        - weekday (int): The index of the weekday to add the lesson to.
        - lesson (Lesson): The Lesson object to add.
        """
        self.weekdays[weekday].addLesson(lesson)

    def removeLesson(self, weekday : int, idx : int):
        """
        Removes a lesson from a specific weekday in the plan.

        Parameters:
        - weekday (int): The index of the weekday to remove the lesson from.
        - idx (int): The index of the lesson to remove.
        """
        self.weekdays[weekday].removeLesson(idx)
    
    def editLesson(self, weekday : int, idx : int, type : str, value):
        """
        Edits a lesson in a specific weekday in the plan.

        Parameters:
        - weekday (int): The index of the weekday to edit the lesson in.
        - idx (int): The index of the lesson to edit.
        - type (str): The type of the lesson attribute to edit.
        - value: The new value of the lesson attribute.
        """
        self.weekdays[weekday].editLesson(idx, type, value)
    
    def status(self):
        """
        Returns the status of the students with this plan.

        Returns:
        - str: The status of the students with this plan.
        """
        weekday = datetime.today().weekday()
        return self.weekdays[weekday].status()
    
    def repeatLessons(self):
        """
        Repeats lessons based on their repeat settings.
        """
        for day in self.weekdays:
            for lesson in day.lessons:
                if lesson.once_in_weeks == 1:
                    continue

                if lesson.repeat_in == 1:
                    lesson.repeat_in = lesson.once_in_weeks
                    lesson.active = False
                elif lesson.repeat_in != 1:
                    lesson.repeat_in -= 1
                
                if lesson.repeat_in == 1:
                    lesson.active = True

from datetime import time, date, datetime

class Activity:
    """
    Represents an activity with a specific beginning time, name, date, description, and list of people.

    Attributes:
        beginning (time): The beginning time of the activity.
        name (str): The name of the activity.
        date (date): The date of the activity.
        description (str, optional): The description of the activity. Defaults to "No description".
        people (list, optional): The list of people associated with the activity. Defaults to an empty list.
    """

    def __init__(self, beginning: time, name: str, date: date, description: str = "No description", people: list = []):
        self.beginning = beginning
        self.name = name
        self.description = description
        self.people = people
        self.date = date

    def __str__(self):
        invited = f'Invited: {", ".join(str(person) for person in self.people)}\n' if len(self.people) > 0 else ''
        return f"{self.name}:\n{self.date.strftime('%d-%m-%Y')} | {str(self.beginning)[:5]}\n> {self.description}\n{invited}"
    
    def getDateTime(self):
        """
        Returns a datetime object representing the date and time of the activity.

        Returns:
            datetime: The datetime object representing the date and time of the activity.
        """
        return datetime(self.date.year, self.date.month, self.date.day, self.beginning.hour, self.beginning.minute)
    
    def __lt__(self, other):
        """
        Compares two Activity objects based on their date and time.

        Args:
            other (Activity): The other Activity object to compare with.

        Returns:
            bool: True if the current Activity is less than the other Activity, False otherwise.
        """
        return self.getDateTime() < other.getDateTime()

class Major:
    """
    Represents a major in a university or educational institution.

    Attributes:
    - name (str): The name of the major.
    - plans (dict): A dictionary containing the study plans for different groups within the major.
    - students (list): A list of student IDs enrolled in the major.
    - sub_groups (list): A list of sub-groups within the major.
    - group_id: The ID of the group the major belongs to.
    - subjects (list): A list of subjects offered in the major.
    """

    def __init__(self, name: str, plans: dict = {}, students: list = [], groups: list = [], group_id=None, subjects: list = []):
        self.name = name
        self.plans = plans
        self.students = students
        self.groups = groups
        self.group_id = group_id
        self.subjects = subjects

    def plan(self, group: str):
        return str(self.plans[group])

    def saveSelf(self):
        file_path = f'{self.group_id}/majors/{self.name}'
        SaveData(file_path, self, 1)

    def Load(path: str):
        return ReadData(path, 1)

    def addGroups(self, groups: list):
        for group in groups:
            self.groups.append(group)
            self.plans[group] = Plan()
        self.saveSelf()

    def removeGroups(self, groups: list):
        for group in groups:
            try:
                self.groups.remove(group)
                del self.plans[group]
            except:
                pass
        self.saveSelf()

    def addStudents(self, students_id: list):
        for student_id in students_id:
            self.students.append(student_id)
        self.saveSelf()

    def removeStudents(self, students_id: list):
        for student_id in students_id:
            try:
                students_id.remove(student_id)
            except:
                pass
        self.saveSelf()

    def addSubjects(self, subjects: list):
        for subject in subjects:
            self.subjects.append(subject)
        self.saveSelf()

    def removeSubjects(self, subjects: list):
        for subject in subjects:
            try:
                self.subjects.remove(subject)
            except:
                pass
        self.saveSelf()

    def addGroup(self, group: str):
        self.groups.append(group)
        self.plans[group] = Plan()
        self.saveSelf()

    def removeGroup(self, group: str):
        try:
            self.groups.remove(group)
            del self.plans[group]
        except:
            pass
        self.saveSelf()

    def addLesson(self, group: str, day: int, lesson: Lesson):
        self.plans[group].addLesson(day, lesson)
        self.saveSelf()

    def removeLesson(self, group: str, day: int, idx: int):
        self.plans[group].removeLesson(day, idx)
        self.saveSelf()
    
    def editLesson(self, group: str, day: int, idx: int, type: str, value):
        self.plans[group].editLesson(day, idx, type, value)
        self.saveSelf()

    def status(self, students):
        status = f"{self.name}\n"
        for group in self.groups:
            group_status = self.plans[group].status()
            for student_id in self.students:
                if students[student_id].group == group:
                    status = f"{status}{students[student_id].nick} : {group_status}\n"
        return status
            

class Role:
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions
    
    def can(self, permission):
        return permission in self.permissions

class Group:
    """
    Represents a group with various attributes and methods.
    """

    def __init__(self, name, gifs=None, stickers=None, id=None, majors=None, groups=None, people=None, activities=None, requests=None, roles=None, weather_cities=None, morning_message_sent=False):
        """
        Initializes a new instance of the Group class.

        Args:
            name (str): The name of the group.
            gifs (dict, optional): A dictionary of GIFs associated with the group. Defaults to None.
            stickers (dict, optional): A dictionary of stickers associated with the group. Defaults to None.
            id (int, optional): The ID of the group. Defaults to None.
            majors (list, optional): A list of majors associated with the group. Defaults to None.
            groups (list, optional): A list of groups associated with the group. Defaults to None.
            people (dict, optional): A dictionary of people associated with the group. Defaults to None.
            activities (list, optional): A list of activities associated with the group. Defaults to None.
            requests (dict, optional): A dictionary of requests associated with the group. Defaults to None.
            roles (list, optional): A list of roles associated with the group. Defaults to None.
        """
        self.id = id
        self.name = name
        self.gifs = gifs or {}
        self.stickers = stickers or {}
        self.majors = majors or []
        self.groups = groups or []
        self.people = people or {}
        self.activities = activities or []
        self.requests = requests or {}
        self.roles = roles or {}
        self.weather_cities = weather_cities or []
        self.morning_message_sent = morning_message_sent
    
    def LoadGroup(self, id):
        return ReadData(f'{id}/group_info', 1)
    
    def saveSelf(self):
        """
        Saves the group information to a file.
        """
        file_path = f'{self.id}/group_info'
        SaveData(file_path, self, 1)
    
    def resetDay(self):
        """
        Resets the morning message status for the day.
        """
        self.morning_message_sent = False
        self.saveSelf()

    def link(self, group_id):
        links = ReadData(f'links', 0) or {}
        links[self.id] = group_id
        SaveData(f'links', links, 0)
    
    def addMajors(self, names):
        """
        Adds majors to the group.

        Args:
            names (list): A list of major names to add.
        """
        for major_name in names:
            if major_name in self.majors:
                continue
            self.majors.append(major_name)
            file_path = f'{self.id}/majors/{major_name}'
            SaveData(file_path, Major(name=major_name, group_id=self.id), 1)
        self.saveSelf()

    def removeMajors(self, names):
        for major_name in names:
            try:
                self.majors.remove(major_name)
            except:
                pass
            file_path = f'{self.id}/majors/{major_name}'
            Delete(file_path, 1)
            self.saveSelf()

    def editMajor(self, idx=None, value=None):
        if idx is None:
            text = "Which major to edit"
            keyboard = ToKeyboard([(f"{i}. {major}", i) for i, major in enumerate(self.majors)], "EDIT_MAJOR")
            return text, keyboard
        else:
            self.majors[idx].name = value
            self.saveSelf()
            return "Done", None

    def listMajors(self):
        return "Majors:\n" + "\n".join(f"{i}. {major}" for i, major in enumerate(self.majors))

    def addPeople(self, people):
        for person in people:
            if person.id in self.people:
                continue
            self.people[person.id] = person
        self.saveSelf()

    def removePeople(self, people_id):
        for person_id in people_id:
            self.people.pop(person_id, None)

    def listPeople(self):
        return "People:\n" + "\n".join(f"{i}. {person} {'(student)' if isinstance(person, Student) else ''}" for i, person in enumerate(self.people.values()))

    def addActivity(self, activity):
        self.activities.append(activity)
        self.activities.sort()
        self.saveSelf()

    def removeActivity(self, idx):
        if 0 <= idx < len(self.activities):
            self.activities.pop(idx)
            self.saveSelf()

    def editActivity(self, idx=None, type=None, value=None) -> tuple[str, InlineKeyboardMarkup]:
        if idx is None:
            text = "Which activity to edit"
            keyboard = ToKeyboard([(f"{i}. {activity.name}", i) for i, activity in enumerate(self.activities)], "EDIT_ACTIVITY")
            return text, keyboard
        elif type is None:
            activity = self.activities[idx]
            text = f"Name: {activity.name}\nDate: {activity.date}\nTime: {activity.beginning}\nDescription: {activity.description}"
            return text, ToKeyboard([("Name", "Name"), ("Date", "Date"), ("Time", "Time"), ("Description", "Description")], f"EDIT_ACTIVITY/{idx}")
        else:
            activity = self.activities[idx]
            if type == "Name":
                activity.name = value
            elif type == "Date":
                activity.date = ToDate(value)
            elif type == "Time":
                activity.beginning = ToTime(value)
            elif type == "Description":
                activity.description = value
            self.saveSelf()
            return "Done", None

    def addLesson(self, major_name=None, day=None, sub_group=None, subject=None, type=None, repeated=None, lesson=None):
        if major_name is None:
            return "Please choose the major: ", ToKeyboard([(f"{i}. {major}", major) for i, major in enumerate(self.majors)], "ADD_LESSON")
        elif day is None:
            return "Please choose the day", ToKeyboard([(f"{i}. {day}", i) for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])], f"ADD_LESSON/{major_name}")
        elif sub_group is None:
            major = Major.Load(f'{self.id}/majors/{major_name}')
            keyboard = ToKeyboard([(f"{group}", group) for group in major.plans.keys()], f"ADD_LESSON/{major_name}/{day}")
            return "Please choose the group", keyboard
        elif subject is None:
            major = Major.Load(f'{self.id}/majors/{major_name}')
            return "Please choose the subject", ToKeyboard([(f"{i}. {subject}", subject) for i, subject in enumerate(major.subjects)], f"ADD_LESSON/{major_name}/{day}/{sub_group}")
        elif type is None:
            return "Please choose the type", ToKeyboard([("Lecture", "Lecture"), ("Seminar", "Seminar"), ("Lab", "Lab"), ("Exercise", "Exercise")], f"ADD_LESSON/{major_name}/{day}/{sub_group}/{subject}")
        elif repeated is None:
            return "Please state if the lesson is every 2 weeks (starting this week)", ToKeyboard([("Yes", "1"), ("No", "0")], f"ADD_LESSON/{major_name}/{day}/{sub_group}/{subject}/{type}")
        else:
            file_path = f'{self.id}/majors/{major_name}'
            major = Major.Load(file_path)
            major.addLesson(sub_group, int(day), lesson)
            major.saveSelf()
            return "Done"

    def removeLesson(self, major_name=None, sub_group=None, day=None, idx=None):
        if major_name is None:
            return "Please choose the major: ", ToKeyboard([(f"{i}. {major}", major) for i, major in enumerate(self.majors)], "REMOVE_LESSON")
        elif sub_group is None:
            major = Major.Load(f'{self.id}/majors/{major_name}')
            keyboard = ToKeyboard([(f"{group}", group) for group in major.plans.keys()], f"REMOVE_LESSON/{major_name}")
            return "Please choose the group", keyboard
        elif day is None:
            major = Major.Load(f'{self.id}/majors/{major_name}')
            return "Please choose the day", ToKeyboard([(f"{i}. {day}", i) for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])], f"REMOVE_LESSON/{major_name}/{sub_group}")
        elif idx is None:
            major = Major.Load(f'{self.id}/majors/{major_name}')
            return "Please choose the lesson to remove", ToKeyboard([(f"{i}. {lesson.subject} - {lesson.type}", i) for i, lesson in enumerate(major.plans[sub_group].weekdays[int(day)].lessons)], f"REMOVE_LESSON/{major_name}/{sub_group}/{day}")
        else:
            major = Major.Load(f'{self.id}/majors/{major_name}')
            major.removeLesson(sub_group, day, idx)
            major.saveSelf()
            return "Done"
    
    def editLesson(self, major_name=None, sub_group=None, day=None, idx=None, type=None, value=None):
        if major_name is None:
            return "Please choose the major: ", ToKeyboard([(f"{i}. {major}", major) for i, major in enumerate(self.majors)], "EDIT_LESSON")
        elif sub_group is None:
            major = Major.Load(f'{self.id}/majors/{major_name}')
            keyboard = ToKeyboard([(f"{group}", group) for group in major.plans.keys()], f"EDIT_LESSON/{major_name}")
            return "Please choose the group", keyboard
        elif day is None:
            major = Major.Load(f'{self.id}/majors/{major_name}')
            return "Please choose the day", ToKeyboard([(f"{i}. {day}", i) for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])], f"EDIT_LESSON/{major_name}/{sub_group}")
        elif idx is None:
            major = Major.Load(f'{self.id}/majors/{major_name}')
            return "Please choose the lesson to edit", ToKeyboard([(f"{i}. {lesson.subject} - {lesson.type}", i) for i, lesson in enumerate(major.plans[sub_group].weekdays[int(day)].lessons)], f"EDIT_LESSON/{major_name}/{sub_group}/{day}")
        elif type is None:
            return "Please choose the attribute to edit", ToKeyboard([("Beginning", "beginning"), ("Ending", "ending"), ("Subject", "subject"), ("Type", "type"), ("Classroom", "classroom"), ("Repeat in", "repeat_in"), ("Once in weeks", "once_in_weeks"), ("Active", "active")], f"EDIT_LESSON/{major_name}/{sub_group}/{day}/{idx}")
        else:
            if type == "subject":
                return "Please choose the subject", ToKeyboard([(f"{i}. {subject}", subject) for i, subject in enumerate(Major.Load(f'{self.id}/majors/{major_name}').subjects)], f"EDIT_LESSON/{major_name}/{sub_group}/{day}/{idx}/{type}")
            elif type == "type":
                return "Please choose the type", ToKeyboard([("Lecture", "Lecture"), ("Seminar", "Seminar"), ("Lab", "Lab"), ("Exercise", "Exercise")], f"EDIT_LESSON/{major_name}/{sub_group}/{day}/{idx}/{type}")
                            
        major = Major.Load(f'{self.id}/majors/{major_name}')
        major.editLesson(sub_group, int(day), idx, type, value)
        major.saveSelf()
        return "Done"

    def listActivities(self, page):
        start_idx = page * 6
        end_idx = start_idx + 6
        activities = self.activities[start_idx:end_idx]
        return "Activities:\n" + "\n".join(f"{i + start_idx}. {activity}" for i, activity in enumerate(activities))

    def listStickers(self, page):
        start_idx = page * 25
        end_idx = start_idx + 25
        stickers = list(self.stickers.keys())[start_idx:end_idx]
        return "Stickers:\n" + "\n".join(f"{i + start_idx}. {sticker}" for i, sticker in enumerate(stickers))

    def listGifs(self, page):
        start_idx = page * 25
        end_idx = start_idx + 25
        gifs = list(self.gifs.keys())[start_idx:end_idx]
        return "Gifs:\n" + "\n".join(f"{i + start_idx}. {gif}" for i, gif in enumerate(gifs))

    def addSubGroups(self, major, sub_groups):
        major = Major.Load(f'{self.id}/majors/{major}')
        for group in sub_groups:
            if group in major.groups:
                continue
            major.addGroup(group)

    def removeGroups(self, major, groups):
        major = Major.Load(f'{self.id}/majors/{major}')
        for group in groups:
            major.removeGroup(group)

    def show(self, params, page=0):
        reply = "Nothing to show"

        try:
            thing_to_show = params[1]
        except IndexError:
            return "What am I supposed to show? (groups/people/activities/plan/stickers/gifs)", None

        arrows = None
        if thing_to_show == "majors":
            reply = self.listMajors()
        elif thing_to_show == "people":
            reply = self.listPeople()
        elif thing_to_show == "activities":
            reply = self.listActivities(page)
            arrows = PageArrows(len(self.activities)//6, page, "a")
        elif thing_to_show == "gifs":
            reply = self.listGifs(page)
            arrows = PageArrows(len(self.gifs)//25, page, "g")
        elif thing_to_show == "stickers":
            reply = self.listStickers(page)
            arrows = PageArrows(len(self.stickers)//25, page, "s")
        elif thing_to_show == "students":
            if len(params) == 2:
                reply = "Students:\n" + "\n".join(f"{i}. {student}" for i, student in enumerate(self.people.values()) if isinstance(student, Student))
            else:
                reply = "Students:\n" + "\n".join(f"{i}. {self.people[student_id]}" for i, student_id in enumerate(Major.Load(f'{self.id}/majors/{params[2]}').students))
        elif thing_to_show == "plan":
            try:
                reply = Major.Load(f'{self.id}/majors/{params[2]}').plan(params[3])
            except IndexError:
                if len(params) == 2:
                    return "Please choose major", ToKeyboard([(f"{i}. {major}", major) for i, major in enumerate(self.majors)], "SHOW_PLAN")
                else:
                    keyboard = ToKeyboard([(f"{group}", group) for group in Major.Load(f'{self.id}/majors/{params[2]}').plans.keys()], f"SHOW_PLAN/{params[2]}")
                    return "Please choose group", keyboard

        return reply, arrows

    def status(self):
        statuses = "\n".join(Major.Load(f'{self.id}/majors/{major}').status(self.people) for major in self.majors)
        if len(statuses) == 0:
            return "No statuses available"
        return statuses
    
    def addSubjects(self, major_name, subjects: list):
        file_path = f'{self.id}/majors/{major_name}'
        major = Major.Load(file_path)
        major.addSubjects(subjects)
        major.saveSelf()

    def removeSubjects(self, major_name, subjects: list):
        file_path = f'{self.id}/majors/{major_name}'
        major = Major.Load(file_path)
        major.removeSubjects(subjects)
        major.saveSelf()

    def appendRole(self, person_name):
        if not hasattr(self, "roles"):
            self.roles = {}
        if len(self.roles) == 0:
            return "Please add a role first", None
        for person in self.people.values():
            if person.nick == person_name.replace("@", ""):
                return "Please choose the role", ToKeyboard([(f"{role.name}", role.name) for role in self.roles.values()], f"ADD_ROLE/{person.id}")
        return "Person not found", None
    
    def removeRole(self, person_name):
        for person in self.people.values():
            if person.nick == person_name.replace("@", ""):
                if len(person.roles) == 0:
                    return "Person has no roles", None
                return "Please choose the role", ToKeyboard([(f"{role}", role) for role in person.roles], f"REMOVE_ROLE/{person.id}")
        return "Person not found", None

    def add(self, params, message):
        try:
            thing_to_add = params[1]
        except IndexError:
            return "What am I supposed to add? (me/them/majors/activity/lesson/groups/subjects/role/city)"

        if thing_to_add == "majors":
            self.addMajors(params[2:])
        elif thing_to_add == "me":
            person = CreatePersonFromUser(message.from_user)
            self.addPeople([person])
        elif thing_to_add == "subjects":
            try:
                self.addSubjects(params[2], params[3:])
            except IndexError:
                return "Please provide major and subjects"
        elif thing_to_add == "groups":
            try:
                if params[2] not in self.majors:
                    return "Please provide a valid major"
                major = params[2]
                self.addSubGroups(major, params[3:])
            except IndexError:
                return "Please provide major and groups"
        elif thing_to_add == "lesson":
            return self.addLesson()
        elif thing_to_add == "them":
            if message.reply_to_message:
                if len(params) == 5:
                    return self.join(params[2], message.reply_to_message.from_user, params[3], params[4])
                elif len(params) == 3:
                    return self.join(params[2], message.reply_to_message.from_user)
                person = CreatePersonFromUser(message.reply_to_message.from_user)
            else:
                return "You didn't reply to anyone"
            self.addPeople([person])
        elif thing_to_add == "gif":
            try:
                name = params[2]
                if message.reply_to_message.animation is None:
                    return "Please reply to a gif"
                file_id = message.reply_to_message.animation.file_id
                self.gifs[name] = file_id
            except IndexError:
                return "Please provide the name for the gif"
        elif thing_to_add == "sticker":
            try:
                name = params[2]
                if message.reply_to_message.sticker is None:
                    return "Please reply to a sticker"
                file_id = message.reply_to_message.sticker.file_id
                self.stickers[name] = file_id
            except IndexError:
                return "Please provide the name for the sticker"
        elif thing_to_add == "activity":
            params = params[2:]
            name = ""

            while ToDate(params[0]) is None:
                name = f"{name} {params[0]}"
                params.pop(0)

            if len(params) >= 3:
                date = ToDate(params[0])
                time = ToTime(params[1])
                description = " ".join(params[2:]) if len(params) > 2 else ""
                if None not in [name, date, time, description]:
                    new_activity = Activity(time, name, date, description)
                    self.addActivity(new_activity)
                else:
                    return "Please state name, date (dd.mm.yyyy), time (00:00), and optionally description"
            else:
                return "Please state name, date (dd.mm.yyyy), time (00:00), and optionally description"
        elif thing_to_add == "role":
            if not hasattr(self, "roles"):
                self.roles = {}
            try:
                name = params[2]
                role = Role(name, [])
                self.roles[name] = role
            except IndexError:
                return "Please provide the name for the role"
        elif thing_to_add == "city":
            try:
                city = params[2]
                self.weather_cities.append(city)
            except IndexError:
                return "Please provide the name of the city"
        else:
            return "(me/them/majors/activity/lesson/groups/subjects/role/city)"

        return "Done"

    def remove(self, params, message):
        try:
            thing_to_remove = params[1]
        except IndexError:
            return "What am I supposed to remove? (me/them/majors/activity/lesson/sticker/gif/role/city)"

        if thing_to_remove == "majors":
            self.removeMajors(params[2:])
        elif thing_to_remove == "me":
            self.removePeople([message.from_user.id])
        elif thing_to_remove == "subjects":
            self.removeSubjects(params[2], params[3:])
        elif thing_to_remove == "them":
            if message.reply_to_message:
                self.removePeople([message.reply_to_message.from_user.id])
            else:
                return "You didn't reply to anyone"
        elif thing_to_remove == "activity":
            try:
                idx = int(params[2])
                self.removeActivity(idx)
            except IndexError or ValueError:
                return "Please state the index of the activity"
        elif thing_to_remove == "lesson":
            return self.removeLesson()
        elif thing_to_remove == "sticker":
            try:
                name = params[2]
                del self.stickers[name]
            except IndexError:
                return "Please provide the tag of the sticker"
        elif thing_to_remove == "gif":
            try:
                name = params[2]
                del self.gifs[name]
            except IndexError:
                return "Please provide the tag of the gif"
        elif thing_to_remove == "role":
            try:
                name = params[2]
                del self.roles[name]
            except IndexError:
                return "Please provide the name of the role"
        elif thing_to_remove == "city":
            try:
                city = params[2]
                self.weather_cities.remove(city)
            except IndexError:
                return "Please provide the name of the city"
        else:
            return "(me/them/majors/activity/lesson/sticker/gif/role/city)"
        return "Done"

    def edit(self, params):
        try:
            thing_to_edit = params[1]
        except IndexError:
            return "What am I supposed to edit? (major/activity/lesson)", None

        if thing_to_edit == "major":
            return self.editMajor()
        elif thing_to_edit == "activity":
            return self.editActivity()
        elif thing_to_edit == "lesson":
            return self.editLesson()
        else:
            return "(major/activity/lesson)", None

    def join(self, group, user, sub_group=None, index=None):
        if group in self.majors:
            if sub_group is None:
                keyboard = ToKeyboard([(f"{group}", group) for group in Major.Load(f'{self.id}/majors/{group}').groups], f"JOIN/{group}")
                return "Please provide the group", keyboard
            major = Major.Load(f'{self.id}/majors/{group}')
            if user.id not in major.students:
                major.addStudents([user.id])
            self.people[user.id] = CreateStudentFromUser(user, group, sub_group, index)
            return "Done", None
    
