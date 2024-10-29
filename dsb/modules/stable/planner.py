""" Planner module for telebot. """

from typing import TYPE_CHECKING
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from dsb.types.lesson import Lesson, str_to_day
from dsb.types.plan import Plan
from dsb.types.module import BaseModule, prevent_edited, admin_only, callback_handler
from dsb.types.errors import DSBError, InvalidValueError
from dsb.utils.transforms import str_to_i
from dsb.utils.button_picker import ButtonPicker
if TYPE_CHECKING:
    from dsb.dsb import DSB

class PlanNotFoundError(DSBError):
    """ Raised when plan is not found """
    def __init__(self, plan_name: str, *args) -> None:
        super().__init__(f"Plan {plan_name} not found", *args)

class PlanAlreadyExistsError(DSBError):
    """ Raised when plan already exists """
    def __init__(self, plan_name: str, *args) -> None:
        super().__init__(f"Plan {plan_name} already exists", *args)

class PlanOwnershipError(DSBError):
    """ Raised when plan ownership is invalid """
    def __init__(self, *args) -> None:
        super().__init__("This plan does not belong to you", *args)

class PlanTransferError(DSBError):
    """ Raised when plan transfer is invalid """
    def __init__(self, plan_name: str, *args) -> None:
        super().__init__(f"Plan {plan_name} already exists in the new group", *args)

class PlanEmptyError(DSBError):
    """ Raised when plan is empty """
    def __init__(self, *args) -> None:
        super().__init__("Plan is empty", *args)

class DoesNotBelongError(DSBError):
    """ Raised when user does not belong to a plan """
    def __init__(self, *args) -> None:
        super().__init__("You do not belong to a plan, use /join_plan to join one", *args)

class NoPlansFoundError(DSBError):
    """ Raised when no plans are found """
    def __init__(self, *args) -> None:
        super().__init__("No plans found", *args)

class LessonNotFoundError(DSBError):
    """ Raised when lesson is not found """
    def __init__(self, *args) -> None:
        super().__init__("Lesson not found", *args)

class NoLessonsError(DSBError):
    """ Raised when no lessons are found """
    def __init__(self, *args) -> None:
        super().__init__("No lessons found", *args)

class NoStudentsError(DSBError):
    """ Raised when no students are found """
    def __init__(self, *args) -> None:
        super().__init__("No students found", *args)

class Planner(BaseModule):
    """ Planner module """
    def __init__(self, ptb, telebot: 'DSB') -> None:
        super().__init__(ptb, telebot)
        self._db = telebot.database
        self._handlers = {
            "create_plan": self._create_plan,
            "delete_plan": self._delete_plan,
            "get_plan": self._get_plan,
            "get_plans": self._get_plans,
            "delete_all": self._delete_all,
            "add_lesson": self._add_lesson,
            "remove_lesson": self._remove_lesson,
            "edit_lesson": self._edit_lesson,
            "clear_day": self._clear_day,
            "clear_all": self._clear_all,
            "edit_plan": self._edit_plan,
            "status": self._status,
            "where_next": self._get_room,
            "join_plan": self._join_plan,
            "leave_plan": self._leave_plan,
            "get_students": self._get_students,
            "transfer_plan": self._transfer_plan,
            "get_owners": self._get_owners,
            "transfer_plan_ownership": self._transfer_plan_ownership,
        }
        self._descriptions = {
            "create_plan": "Create a new lesson plan",
            "delete_plan": "Delete a lesson plan",
            "get_plan": "Get a lesson plan",
            "get_plans": "Get all lesson plans",
            "delete_all": "Delete all lesson plans",
            "add_lesson": "Add a lesson to a plan",
            "remove_lesson": "Remove a lesson from a plan",
            "edit_lesson": "Edit a lesson in a plan",
            "clear_day": "Clear all lessons for a day",
            "clear_all": "Clear all lessons for a plan",
            "edit_plan": "Edit a plan name",
            "status": "Get status of all students in the group",
            "where_next": "Send room you have lessons in next",
            "join_plan": "Join a lesson plan",
            "leave_plan": "Leave a lesson plan",
            "get_students": "Get all students in a plan",
            "transfer_plan": "Transfer a plan to another group",
            "get_owners": "Get all plan owners (Admins only)",
            "transfer_plan_ownership": "Transfer plan ownership"
        }
        self._callback_handlers = {
            "^delete_plan:": self._delete_plan_callback,
            "^clear_day:": self._clear_day_callback,
            "^join_plan:": self._join_plan_callback,
            "^transfer_plan_ownership:": self._transfer_plan_ownership,
            "^remove_lesson:": self._remove_lesson_callback
        }

    def __is_owner(self, plan: Plan, user_id: int) -> bool:
        return user_id == plan.owner or str(user_id) in self.config["admins"]

    def __create_plan(self, name: str, group_id: int, user_id: int):
        """ Create a new lesson plan """
        new_plan = Plan(user_id)
        plans = self._db.get_table("plans")
        if not all((name, group_id, new_plan)):
            raise InvalidValueError("name")
        if plans.get_row((name, group_id)):
            raise PlanAlreadyExistsError(name)
        plans.add_row([name, group_id, new_plan])
        plans.save()

    def __transfer_plan(self, plan_name: str, plan: Plan, new_group: int, force: bool) -> None:
        """ Transfer plan to another group """
        if not plan:
            raise PlanNotFoundError(plan_name)

        if not new_group:
            raise InvalidValueError("new_group")

        existing_plan = self.__get_plan(plan_name, new_group)

        if not force and existing_plan:
            raise PlanAlreadyExistsError(plan_name)

        if not existing_plan:
            self.__create_plan(plan_name, new_group, new_group)

        self.__update_plan(plan_name, new_group, plan)

    def __get_plan(self, name: str, group_id: int) -> Plan | None:
        """ Get a lesson plan """
        plans = self._db.get_table("plans")
        row = plans.get_row((name, group_id))
        if not row:
            return None
        return row[3]

    def __delete_plan(self, name: str, group_id: int, user_id: int) -> None:
        """ Delete a lesson plan """
        plan = self.__get_plan(name, group_id)

        if plan is None:
            raise PlanNotFoundError(name)

        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        plans = self._db.get_table("plans")
        plans.remove_row((name, group_id))
        plans.save()

    def __get_plans(self, group_id: int) -> dict[str, Plan]:
        """ Get all lesson plans """
        plans = self._db.get_table("plans")
        group_plans = plans.get_rows(check_function=lambda x: x[2] == group_id)
        return {plan[1]: plan[3] for plan in group_plans}

    def __update_plan(self, name: str, group_id: int, new_plan: Plan, new_name: str = "") -> bool:
        """ Update a lesson plan """
        plans = self._db.get_table("plans")
        plan = plans.get_row((name, group_id))
        if not plan:
            return False
        if new_name:
            plan[1] = new_name
        plan[3] = new_plan
        plans.remove_row((name, group_id))
        plans.add_row(plan[1:])
        plans.save()
        return True

    def __get_status(self, group_id: int) -> tuple[list[tuple[str, str]]]:
        """ Return complete status of all students in a group """
        plans = self.__get_plans(group_id)

        if not plans:
            raise NoPlansFoundError()

        free_students = []
        busy_students = []
        for plan in plans.values():
            if plan.is_free():
                next_lesson = plan.next_lesson
                if not next_lesson:
                    text = "No lessons left"
                else:
                    diff = next_lesson.time_until.total_seconds()
                    text = f"{int(diff // 3600)}h {int(diff//60 % 60):02}min"
                for student in plan.students:
                    free_students.append((student, text))
            else:
                current_lesson = plan.current_lesson
                diff = current_lesson.time_left.total_seconds()
                lesson_info = f"{current_lesson.subject} | {current_lesson.type}\n"
                text = f"{int(diff // 3600)}h {int(diff//60 % 60):02}min"
                for student in plan.students:
                    busy_students.append((student, lesson_info + text))

        return free_students, busy_students

    def __get_plan_name(self, context: ContextTypes.DEFAULT_TYPE) -> str:
        """ Get plan name from update """
        if not context.args:
            return None

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        return plan_name

    def __get_plan_from_update(self, update: Update,
                               context: ContextTypes.DEFAULT_TYPE) -> tuple[str, Plan]:
        """ Returns plan name, plan object and kwargs """
        if not context.args:
            return None, None

        plan_name = self.__get_plan_name(context)

        group_id = update.effective_chat.id
        plan = self.__get_plan(plan_name, group_id)

        return plan_name, plan

    @prevent_edited
    async def _create_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Create a new lesson plan 

        Usage: /create_plan <name>

        Command parameters
        -----------
        name : str
            Name of the plan
        """
        plan_name = self.__get_plan_name(context)
        group_id = update.effective_chat.id

        self.__create_plan(plan_name, group_id, update.effective_user.id)

        await self._like(update)

    @callback_handler
    async def _delete_plan_callback(self, update: Update,
                                    context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Callback for plan deletion """
        data = update.callback_query.data
        group_id = update.effective_chat.id
        user_id = update.effective_user.id

        plan_name = data.split(":")[1]
        self.__delete_plan(plan_name, group_id, user_id)
        await context.bot.delete_message(update.effective_chat.id,
                                           update.effective_message.message_id)
        await context.bot.send_message(update.effective_chat.id, "Plan deleted")

    @prevent_edited
    async def _delete_plan(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Delete a lesson plan

        """
        group_id = update.effective_chat.id

        plans = self.__get_plans(group_id)
        user_id = update.effective_user.id
        picker = ButtonPicker([{name: name} for name,
                               plan in plans.items() if self.__is_owner(plan, user_id)],
                              "delete_plan")
        if picker.is_empty:
            raise NoPlansFoundError()
        await update.message.reply_text("Choose a plan to delete:", reply_markup=picker)

    @prevent_edited
    async def _get_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Get a lesson plan

        Usage: /get_plan <name> or /get_plan

        Command parameters
        -----------
        name : str (optional)
            Name of the plan, if not provided, will get the plan of the user
        """
        plan_name, plan = self.__get_plan_from_update(update, context)
        group_id = update.effective_chat.id

        if plan_name is not None and not plan:
            raise PlanNotFoundError(plan_name)

        if not plan:
            plans = self._db.get_table("plans")
            username = update.message.from_user.username
            row = plans.get_row(check_function=lambda x: x[2] == group_id and
                                 username in x[3].students)
            if not row:
                raise DoesNotBelongError()
            plan: Plan = row[3]
            plan_name = row[1]

        if plan.is_empty():
            raise PlanEmptyError()

        plan_image = plan.to_image(plan_name)
        await update.message.reply_photo(plan_image)

    @prevent_edited
    async def _get_plans(self, update: Update, _) -> None:
        """
        Get all lesson plans in the group

        """
        group_id = update.effective_chat.id
        plans = self.__get_plans(group_id)
        plans_str = "Plans:\n"

        for i, plan in enumerate(plans.items()):
            students = plan[1].students
            if not students:
                students = ["No students in the plan"]
            plans_str += f"{i+1}. {plan[0]}\n{'\n'.join(students)}\n"

        if not plans:
            raise NoPlansFoundError()

        await update.message.reply_text(plans_str)

    @admin_only
    @prevent_edited
    async def _delete_all(self, update: Update, _) -> None:
        """
        Delete all lesson plans in the group

        """
        group_id = update.effective_chat.id
        plans = self.__get_plans(group_id)
        user_id = update.effective_user.id

        for plan in plans:
            try:
                self.__delete_plan(plan, group_id, user_id)
            except DSBError:
                continue

        await self._like(update)

    @prevent_edited
    async def _add_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Add a lesson to a plan

        Usage: /add_lesson <plan_name> --day <day> --subject <subject> 
        --teacher <teacher> --room <room> --start <start> --end <end> --type <type>

        Command parameters
        -----------
        day : int
            Day of the lesson, 1-5 or monday-friday
        subject : str
            Subject of the lesson
        teacher : str
            Teacher of the lesson
        room : str
            Room of the lesson
        start : str
            Start time of the lesson
        end : str
            End time of the lesson
        type : str
            Type of the lesson
        """
        _, kwargs = self._get_args(context)
        plan_name, plan = self.__get_plan_from_update(update, context)

        if not plan:
            raise PlanNotFoundError(plan_name)

        new_lesson = Lesson(kwargs)

        group_id = update.effective_chat.id

        plan.add_lesson(new_lesson.day - 1, new_lesson)
        self.__update_plan(plan_name, group_id, plan)
        await self._like(update)

    @callback_handler
    async def _remove_lesson_callback(self, update: Update,
                                      context: ContextTypes.DEFAULT_TYPE) -> None:
        data = update.callback_query.data
        group_id = update.effective_chat.id
        day = str_to_day(data.split(":")[1])
        plan_name = data.split(":")[2]
        plan = self.__get_plan(plan_name, group_id)
        if not self.__is_owner(plan, update.effective_user.id):
            raise PlanOwnershipError()
        if len(data.split(":")) < 4:
            lessons = plan.get_day(day-1)
            picker = ButtonPicker([{f"{lesson.subject}: {lesson.type}":
                                    f"{data.replace("remove_lesson:", "")}:{i}"} for i,
                                   lesson in enumerate(lessons)], "remove_lesson")
            if picker.is_empty:
                raise NoLessonsError()
            await update.effective_message.edit_text("Pick a lesson to remove", reply_markup=picker)
            return
        idx = str_to_i(data.split(":")[3])
        plan.remove_lesson_by_index(day - 1, idx)
        self.__update_plan(plan_name, group_id, plan)
        await context.bot.delete_message(group_id, update.effective_message.id)
        await context.bot.send_message(group_id, "Lesson removed")

    @prevent_edited
    async def _remove_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Remove a lesson from a plan

        Usage: /remove_lesson <plan_name>
        """
        plan_name, plan = self.__get_plan_from_update(update, context)

        if not plan:
            raise PlanNotFoundError(plan_name)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        picker = ButtonPicker([{day: f"{i+1}:{plan_name}"} for i,
                               day in enumerate(days)], "remove_lesson")
        await update.message.reply_text("Pick a day to remove a lesson", reply_markup=picker)

    @prevent_edited
    async def _edit_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Edit a lesson in a plan

        Usage: /edit_lesson <plan_name> --idx <idx> --day <day>...

        Command parameters
        -----------
        idx : int
            Index of the lesson, counting from 0
        day : int
            Day of the lesson, 1-5 or monday-friday
        new_day : int
            New day of the lesson, 1-5 or monday-friday
        subject : str
            Subject of the lesson
        teacher : str
            Teacher of the lesson
        room : str
            Room of the lesson
        start : str
            Start time of the lesson
        end : str
            End time of the lesson
        type : str
            Type of the lesson
        """
        _, kwargs = self._get_args(context)
        plan_name, plan = self.__get_plan_from_update(update, context)

        if not plan:
            raise PlanNotFoundError(plan_name)

        user_id = update.effective_user.id
        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        idx = str_to_i(kwargs.get("idx", ""))
        day = str_to_day(kwargs.get("day", ""))
        new_day = str_to_day(kwargs.get("new_day", ""))

        if not idx:
            raise InvalidValueError("idx")

        if not day:
            raise InvalidValueError("day")

        lessons = plan.get_day(day - 1)
        if not lessons:
            await update.message.reply_text("No lessons for this day")
            return

        try:
            lesson = lessons[idx]
        except IndexError as exc:
            raise LessonNotFoundError() from exc

        if new_day:
            kwargs["day"] = kwargs["new_day"]

        lesson_data = lesson.to_dict()
        lesson_data.update(kwargs)

        new_lesson = Lesson(lesson_data)

        plan.remove_lesson_by_index(day - 1, idx)
        plan.add_lesson(new_day - 1 if new_day else day - 1, new_lesson)
        self.__update_plan(plan_name, update.effective_chat.id, plan)
        await self._like(update)

    @callback_handler
    async def _clear_day_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        data = update.callback_query.data
        plan_name = data.split(data.split(":")[1])
        day = str_to_day(data.split(":")[2])
        group_id = update.effective_chat.id
        plan = self.__get_plan(plan_name, group_id)
        plan.clear_day(day)
        self.__update_plan(plan_name, group_id, plan)
        await context.bot.delete_message(group_id, update.message.id)
        await context.bot.send_message(group_id, "Day cleared")

    @prevent_edited
    async def _clear_day(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Clear all lessons for a day
        
        Usage: /clear_day <plan_name>
        """
        plan_name, plan = self.__get_plan_from_update(update, context)

        if not plan:
            raise PlanNotFoundError(plan_name)

        user_id = update.effective_user.id
        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        picker = ButtonPicker([{day: f"{i+1}"} for i, day in enumerate(days)], "clear_day")
        await update.message.reply_text("Pick a day to clear", reply_markup=picker)

    @prevent_edited
    async def _clear_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Clear all lessons for a plan
        
        Usage: /clear_all <plan_name>
        """
        plan_name, plan = self.__get_plan_from_update(update, context)
        group_id = update.effective_chat.id

        if not plan:
            raise PlanNotFoundError(plan_name)

        plan.clear_all()
        self.__update_plan(plan_name, group_id, plan)
        await self._like(update)

    @prevent_edited
    async def _edit_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Editing a plan name

        Usage: /edit_plan <plan_name> --new_name <new_name>
        
        Command parameters
        -----------
        new_name : str
            New name of the plan
        """
        group_id = update.effective_chat.id
        _, kwargs = self._get_args(context)
        plan_name, plan = self.__get_plan_from_update(update, context)

        if plan is None:
            raise PlanNotFoundError(plan_name)

        user_id = update.effective_user.id
        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        self.__update_plan(plan_name, group_id, plan, kwargs.get("new_name"))
        await self._like(update)

    @prevent_edited
    async def _status(self, update: Update, _) -> None:
        """
        Get status of all students in this group

        """
        today = datetime.today().weekday() + 1
        if today > 5:
            await update.message.reply_text("No lessons tooday")
            return

        free_students, busy_students = self.__get_status(update.effective_chat.id)

        student_list = "Free right now:\n" + \
            "\n".join(f"{student} - {text}" for student, text in free_students) + \
            "\n\nBusy right now: \n" + \
            "\n".join(f"{student} - {text}" for student, text in busy_students)

        await update.message.reply_text(student_list)

    @prevent_edited
    async def _get_room(self, update: Update, _) -> None:
        """
        Send room you have lessons in next

        """
        plans = self.__get_plans(update.effective_chat.id)

        if not plans:
            raise NoPlansFoundError()

        group_id = update.effective_chat.id
        plans = self._db.get_table("plans")
        username = update.message.from_user.username

        row = plans.get_row(check_function=lambda x: x[2] == group_id and
                                username in x[3].students)
        if not row:
            raise DoesNotBelongError()

        plan: Plan = row[3]
        lesson = plan.next_lesson
        if not lesson:
            await update.message.reply_text("You don't have any lesson next")
            return
        await update.message.reply_text(f"You have your next lesson in {lesson.room}")

    @callback_handler
    async def _join_plan_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        data = update.callback_query.data
        group_id = update.effective_chat.id
        plan_name = data.split(":")[1]
        plan = self.__get_plan(plan_name, group_id)
        if not plan:
            raise PlanNotFoundError(plan_name)
        plans = self.__get_plans(group_id)
        for name, current_plan in plans.items():
            if update.effective_user.username in current_plan.students:
                current_plan.remove_student(update.effective_user.username)
                self.__update_plan(name, group_id, current_plan)
                break
        plan.add_student(update.effective_user.username)
        self.__update_plan(plan_name, group_id, plan)
        await context.bot.delete_message(group_id, update.effective_message.id)
        await context.bot.send_message(group_id, f"You have joined {plan_name}")

    @prevent_edited
    async def _join_plan(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Join a lesson plan
        
        Usage: /join_plan <plan_name>
        """
        plans = self.__get_plans(update.effective_chat.id)
        user_id = update.effective_user.id
        picker = ButtonPicker([{name: name} for name, plan in plans.items()
                               if user_id not in plan.students], "join_plan")
        if picker.is_empty:
            raise NoPlansFoundError()
        await update.message.reply_text("Choose a plan to join:", reply_markup=picker)

    @prevent_edited
    async def _leave_plan(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Leave a lesson plan
        
        Usage: /leave_plan
        """
        group_id = update.effective_chat.id
        plans = self.__get_plans(group_id)
        for name, current_plan in plans.items():
            if update.effective_user.username not in current_plan.students:
                continue
            current_plan.remove_student(update.effective_user.username)
            self.__update_plan(name, group_id, current_plan)
            await self._like(update)
            return
        await update.message.reply_text("You are not in any plan")

    @prevent_edited
    async def _transfer_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ 
        Transfer a plan to another group 
        
        Command parameters
        -----------
        new_group : int
            Group to transfer the plan to
        force : optional
            Force plan transfer, will overwrite the existing plan with the same name
        """
        _, kwargs = self._get_args(context)
        plan_name, plan = self.__get_plan_from_update(update, context)
        new_group = str_to_i(kwargs.get("new_group", ""))

        self.__transfer_plan(plan_name, plan, new_group, kwargs.get("force", False))

        await self._like(update)

    @admin_only
    @prevent_edited
    async def _get_owners(self, update: Update, _) -> None:
        """
        Get all plan owners
        
        """
        group_id = update.effective_chat.id
        plans = self.__get_plans(group_id)
        owners = "\n".join(f"{plan[0]} - {plan[1].owner}" for plan in plans.items())
        if not owners:
            raise NoPlansFoundError()
        await update.message.reply_text(owners)

    @prevent_edited
    async def _get_students(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Get all students in a plan
        
        Usage: /get_students <plan_name>
        """
        plan_name, plan = self.__get_plan_from_update(update, context)

        if not plan:
            raise PlanNotFoundError(plan_name)

        student_list = "\n".join(f"{i+1}. {student}" for i, student in enumerate(plan.students))
        if not student_list:
            raise NoStudentsError()

        await update.message.reply_text(f"Students:\n{student_list}")

    @prevent_edited
    async def _transfer_plan_ownership(self, update: Update,
                                       context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Transfer plan ownership
        
        Usage: /transfer_plan_ownership <plan_name> --new_owner <new_owner>

        Command parameters
        -----------
        new_owner : int
            New owner of the plan
        """
        _, kwargs = self._get_args(context)
        plan_name, plan = self.__get_plan_from_update(update, context)

        group_id = update.effective_chat.id

        if not plan:
            raise PlanNotFoundError(plan_name)

        user_id = update.effective_user.id
        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        if "new_owner" not in kwargs:
            raise InvalidValueError("new_owner")

        new_owner = str_to_i(kwargs.get("new_owner"))

        plan.owner = new_owner
        self.__update_plan(plan_name, group_id, plan)
        await self._like(update)

    def prepare(self):
        self._db.add_table("plans", [("name", str, True),
                                     ("group_id", int, True),
                                     ("plan", Plan, False)], True)
        return super().prepare()
