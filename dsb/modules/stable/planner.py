""" Planner module for telebot. """

import copy
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
    from dsb.engine import DSBEngine

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
    def __init__(self, ptb, telebot: 'DSBEngine') -> None:
        super().__init__(ptb, telebot)
        self._handlers = {
            "create_plan": self._create_plan,
            "delete_plan": self._delete_plan,
            "get_plan": self._get_plan,
            "plan": self._get_plan,
            "get_plans": self._get_plans,
            "delete_all": self._delete_all,
            "add_lesson": self._add_lesson,
            "remove_lesson": self._remove_lesson,
            "edit_lesson": self._edit_lesson,
            "clear_day": self._clear_day,
            "clear_all": self._clear_all,
            "edit_plan": self._edit_plan,
            "status": self._status,
            "where_next": self._get_roomnxt,
            "where_now": self._get_roomnow,
            "join_plan": self._join_plan,
            "leave_plan": self._leave_plan,
            "get_students": self._get_students,
            "copy_plan": self._copy_plan,
            "paste_plan": self._paste_plan,
            "get_owners": self._get_owners,
            "transfer_plan_ownership": self._transfer_plan_ownership,
        }
        self._descriptions = {
            "create_plan": "Create a new lesson plan",
            "delete_plan": "Delete a lesson plan",
            "get_plan": "Get a lesson plan",
            "plan": "Get a lesson plan",
            "get_plans": "Get all lesson plans",
            "delete_all": "Delete all lesson plans",
            "add_lesson": "Add a lesson to a plan",
            "remove_lesson": "Remove a lesson from a plan",
            "edit_lesson": "Edit a lesson in a plan",
            "clear_day": "Clear all lessons for a day",
            "clear_all": "Clear all lessons for a plan",
            "edit_plan": "Edit a plan name",
            "status": "Get status of all students in the group",
            "where_next": "Send room you have lesson in next",
            "where_now": "Send room you have your lesson in now",
            "join_plan": "Join a lesson plan",
            "leave_plan": "Leave a lesson plan",
            "get_students": "Get all students in a plan",
            "copy_plan": "Copy plan",
            "paste_plan": "Paste plan",
            "get_owners": "Get all plan owners (Admins only)",
            "transfer_plan_ownership": "Transfer plan ownership"
        }
        self._callback_handlers = {
            "^delete_plan:": self._delete_plan_callback,
            "^clear_day:": self._clear_day_callback,
            "^join_plan:": self._join_plan_callback,
            "^remove_lesson:": self._remove_lesson_callback,
            "^get_students": self._get_students_callback,
            "^get_plan:": self._get_plan_callback,
        }

    def __is_owner(self, plan: Plan, user_id: int) -> bool:
        return user_id == plan.owner or user_id in self._dsb.admins

    def __create_plan(self, update: Update,
                      context: ContextTypes.DEFAULT_TYPE,
                      plan_name: str) -> None:
        """ Create a new lesson plan """
        if "plans" not in context.chat_data:
            context.chat_data["plans"] = {}
        if plan_name in context.chat_data["plans"]:
            raise PlanAlreadyExistsError(plan_name)
        context.chat_data["plans"].update({plan_name: Plan(update.effective_user.id)})

    def __delete_plan(self, context: ContextTypes.DEFAULT_TYPE, plan_name: str) -> None:
        """ Delete a lesson plan """
        if plan_name not in context.chat_data.get("plans", {}):
            raise PlanNotFoundError(plan_name)
        context.chat_data.get("plans", {}).pop(plan_name, None)

    def __get_plans(self, context: ContextTypes.DEFAULT_TYPE) -> dict[str, Plan]:
        """ Get all lesson plans """
        return context.chat_data.get("plans", {})

    def __get_status(self, context: ContextTypes.DEFAULT_TYPE) -> tuple[list[tuple[str, str]]]:
        """ Return complete status of all students in a group """
        plans = self.__get_plans(context)

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
        args, _ = self._get_args(context)
        return " ".join(args)

    def __get_plan(self, context: ContextTypes.DEFAULT_TYPE, plan_name: str) -> Plan:
        """ Get plan by name """
        plan = context.chat_data.get("plans", {}).get(plan_name, None)
        if not plan:
            raise PlanNotFoundError(plan_name)
        return plan

    def __get_plan_from_update(self, _: Update,
                               context: ContextTypes.DEFAULT_TYPE) -> tuple[str, Plan]:
        """ Returns plan name, plan object and kwargs """
        args, _ = self._get_args(context)
        plan_name = " ".join(args)
        plan = self.__get_plan(context, plan_name)
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
        self.__create_plan(update, context, plan_name)
        await self._like(update)

    @callback_handler
    async def _delete_plan_callback(self, update: Update,
                                    context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Callback for plan deletion """
        data = update.callback_query.data
        plan_name = data.split(":")[1]
        self.__delete_plan(context, plan_name)
        await context.bot.delete_message(update.effective_chat.id,
                                           update.effective_message.message_id)
        await context.bot.send_message(update.effective_chat.id, "Plan deleted")

    @prevent_edited
    async def _delete_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Delete a lesson plan

        Usage: /delete_plan
        """
        plans = self.__get_plans(context)
        user_id = update.effective_user.id
        picker = ButtonPicker([{name: name} for name,
                               plan in plans.items() if self.__is_owner(plan, user_id)],
                              "delete_plan", user_id=user_id)
        if picker.is_empty:
            raise NoPlansFoundError()
        await update.message.reply_text("Choose a plan to delete:", reply_markup=picker)

    @callback_handler
    async def _get_plan_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        data = update.callback_query.data
        group_id = update.effective_chat.id
        plan_name = data.split(":")[1]
        plan = self.__get_plan(context, plan_name)
        if not plan:
            raise PlanNotFoundError(plan_name)
        await context.bot.delete_message(group_id, update.effective_message.id)
        plan_image = plan.to_image(plan_name)
        if not plan_image:
            raise PlanEmptyError()
        await context.bot.send_photo(group_id, photo=plan_image)

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
        try:
            plan_name, plan = self.__get_plan_from_update(update, context)
        except PlanNotFoundError as e:
            if update.message.text.startswith("/get_plan"):
                plans = context.chat_data.get("plans", {})
                if not plans:
                    raise NoPlansFoundError() from e
                picker = ButtonPicker([{plan: f"{plan}:{update.effective_user.id}"}
                                    for plan in plans],"get_plan", user_id=update.effective_user.id)
                await update.message.reply_text("Choose a plan to get:", reply_markup=picker)
                return
            plans = context.chat_data.get("plans", {})
            username = update.message.from_user.username
            for plan_name, plan in plans.items():
                if username in plan.students:
                    break

        if plan.is_empty():
            raise PlanEmptyError()

        plan_image = plan.to_image(plan_name)
        await update.message.reply_photo(plan_image)

    @prevent_edited
    async def _get_plans(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Get all lesson plans in the group

        """
        plans = self.__get_plans(context)
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
    async def _delete_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Delete all lesson plans in the group

        """
        context.chat_data["plans"].clear()
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
        weeks : "even" or "odd"
            Repeat the lesson every even or odd week
        """
        _, kwargs = self._get_args(context)
        plan_name, plan = self.__get_plan_from_update(update, context)

        if not plan:
            raise PlanNotFoundError(plan_name)

        new_lesson = Lesson(kwargs)

        plan.add_lesson(new_lesson.day - 1, new_lesson)
        await self._like(update)

    @callback_handler
    async def _remove_lesson_callback(self, update: Update,
                                      context: ContextTypes.DEFAULT_TYPE) -> None:
        data = update.callback_query.data
        group_id = update.effective_chat.id
        plan_name = data.split(":")[1]

        if len(data.split(":")) < 4:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            picker = ButtonPicker([{day: f"{plan_name}:{day}"} for day in days],
                                "remove_lesson", user_id=update.effective_user.id)
            await update.effective_message.edit_text("Pick a day to remove lessons from",
                                                    reply_markup=picker)
            return
        day = str_to_day(data.split(":")[2])
        plan = self.__get_plan(context, plan_name)
        if len(data.split(":")) < 5:
            lessons = plan.get_day(day-1)
            picker = ButtonPicker([{f"{lesson.subject}: {lesson.type}":
                                    f"{data.replace("remove_lesson:", "")}:{i}"} for i,
                                   lesson in enumerate(lessons)], "remove_lesson",
                                  user_id=update.effective_user.id)
            if picker.is_empty:
                raise NoLessonsError()
            await update.effective_message.edit_text("Pick a lesson to remove", reply_markup=picker)
            return
        idx = str_to_i(data.split(":")[3])
        plan.remove_lesson_by_index(day - 1, idx)
        await context.bot.delete_message(group_id, update.effective_message.id)
        await context.bot.send_message(group_id, "Lesson removed")

    @prevent_edited
    async def _remove_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Remove a lesson from a plan

        Usage: /remove_lesson <plan_name>
        """
        plans = self.__get_plans(context)
        plan_names = [name for name, plan in plans.items()
                 if self.__is_owner(plan, update.effective_user.id)]
        user_id = update.effective_user.id
        picker = ButtonPicker([{name: name} for name in plan_names],
                              "remove_lesson", user_id=user_id)
        if picker.is_empty:
            raise DSBError("You do not own any plans")
        await update.message.reply_text("Pick a plan you want to remove a lesson from",
                                        reply_markup=picker)

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
        weeks : "even" or "odd"
            Repeat the lesson every even or odd week
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

        if idx is None:
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
        await self._like(update)

    @callback_handler
    async def _clear_day_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        data = update.callback_query.data
        if len(data.split(":")) < 3:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            picker = ButtonPicker([{day: f"{data.replace("clear_day:", "")}:{day}"}
                                   for day in days], "clear_day", user_id=update.effective_user.id)
            if picker.is_empty:
                raise NoLessonsError()
            await update.effective_message.edit_text("Pick a day to clear", reply_markup=picker)
            return
        plan_name = data.split(":")[1]
        day = str_to_day(data.split(":")[2])
        group_id = update.effective_chat.id
        plan = self.__get_plan(context, plan_name)
        plan.clear_day(day - 1)
        await context.bot.delete_message(group_id, update.effective_message.id)
        await context.bot.send_message(group_id, "Day cleared")

    @prevent_edited
    async def _clear_day(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Clear all lessons for a day
        
        Usage: /clear_day
        """
        plans = self.__get_plans(context)
        user_id = update.effective_user.id
        picker = ButtonPicker([{name: name} for name, plan in plans.items()
                                 if self.__is_owner(plan, user_id)], "clear_day",
                              user_id=user_id)
        if picker.is_empty:
            raise NoPlansFoundError()
        await update.message.reply_text("Choose a plan to clear", reply_markup=picker)

    @callback_handler
    async def _clear_all_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        data = update.callback_query.data
        plan_name = data.split(":")[1]
        group_id = update.effective_chat.id
        plan = context.chat_data["plans"].get(plan_name, None)
        plan.clear_all()
        await context.bot.delete_message(group_id, update.message.id)
        await context.bot.send_message(group_id, "All lessons cleared")

    @prevent_edited
    async def _clear_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Clear all lessons for a plan
        
        Usage: /clear_all
        """
        plans = self.__get_plans(context)
        user_id = update.effective_user.id
        picker = ButtonPicker([{name: name} for name, plan in plans.items()
                                 if self.__is_owner(plan, user_id)], "clear_all",
                              user_id=user_id)
        if picker.is_empty:
            raise NoPlansFoundError()
        await update.message.reply_text("Choose a plan to clear", reply_markup=picker)

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
        _, kwargs = self._get_args(context)
        plan_name, plan = self.__get_plan_from_update(update, context)

        if plan is None:
            raise PlanNotFoundError(plan_name)

        user_id = update.effective_user.id
        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        new_name = kwargs.get("new_name", None)
        if new_name is None:
            raise InvalidValueError("new_name")
        context.chat_data["plans"][new_name] = context.chat_data["plans"].pop(plan_name)

        await self._like(update)

    @prevent_edited
    async def _status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Get status of all students in this group

        """
        today = datetime.today().weekday() + 1
        if today > 5:
            await update.message.reply_text("No lessons today")
            return

        free_students, busy_students = self.__get_status(context)

        student_list = "Free right now:\n" + \
            "\n".join(f"{student} - {text}" for student, text in free_students) + \
            "\n\nBusy right now: \n" + \
            "\n".join(f"{student} - {text}" for student, text in busy_students)

        await update.message.reply_text(student_list)

    @prevent_edited
    async def _get_roomnxt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Send room you have lessons in next

        """
        group_id = update.effective_chat.id
        plan_name =  context.user_data.get(f"{group_id}_plan_name", None)
        if plan_name is not None:
            plan = context.chat_data["plans"].get(plan_name, None)
        else:
            raise DoesNotBelongError()
        lesson = plan.next_lesson
        if not lesson:
            await update.message.reply_text("You don't have any lesson next")
            return
        await update.message.reply_text(f"You have your next lesson in {lesson.room}")

    @prevent_edited
    async def _get_roomnow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Send room you have lessons in now

        """
        group_id = update.effective_chat.id
        plan_name =  context.user_data.get(f"{group_id}_plan_name", None)
        if plan_name is not None:
            plan = context.chat_data["plans"].get(plan_name, None)
        else:
            raise DoesNotBelongError()
        lesson = plan.current_lesson
        if not lesson:
            await update.message.reply_text("You don't have any lesson now")
            return
        await update.message.reply_text(f"You have your lesson in {lesson.room}")

    @callback_handler
    async def _join_plan_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        data = update.callback_query.data
        group_id = update.effective_chat.id
        plan_name = data.split(":")[1]
        plan = context.chat_data["plans"].get(plan_name, None)
        if not plan:
            raise PlanNotFoundError(plan_name)
        plans = self.__get_plans(context)
        for current_plan in plans.values():
            if update.effective_user.username in current_plan.students:
                current_plan.remove_student(update.effective_user.username)
                break
        plan.add_student(update.effective_user.username)
        context.user_data[f"{group_id}_plan_name"] = plan_name
        await context.bot.delete_message(group_id, update.effective_message.id)
        await context.bot.send_message(group_id, f"You have joined {plan_name}")

    @prevent_edited
    async def _join_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Join a lesson plan
        
        Usage: /join_plan
        """
        plans = self.__get_plans(context)
        user_id = update.effective_user.id
        picker = ButtonPicker([{name: name} for name, plan in plans.items()
                               if user_id not in plan.students], "join_plan",
                              user_id=user_id)
        if picker.is_empty:
            raise NoPlansFoundError()
        await update.message.reply_text("Choose a plan to join:", reply_markup=picker)

    @prevent_edited
    async def _leave_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Leave a lesson plan
        
        Usage: /leave_plan
        """
        plans = self.__get_plans(context)
        for current_plan in plans.values():
            if update.effective_user.username not in current_plan.students:
                continue
            current_plan.remove_student(update.effective_user.username)
            await self._like(update)
            return
        await update.message.reply_text("You are not in any plan")

    @prevent_edited
    async def _copy_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Copy a plan to the user data
        
        Usage: /copy_plan <plan_name>
        """
        plan_name, plan = self.__get_plan_from_update(update, context)
        if not plan:
            raise PlanNotFoundError(plan_name)
        context.user_data["saved_plan"] = (plan_name, copy.deepcopy(plan))
        await self._like(update)

    @prevent_edited
    async def _paste_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Paste a plan from the user data and save it in the group data
        
        Usage: /paste_plan or /paste_plan <plan_name>
        """
        if "saved_plan" not in context.user_data:
            raise DSBError("No plan saved")
        args, _ = self._get_args(context)
        plan_name, plan = context.user_data["saved_plan"]
        plan_name = " ".join(args) if args else plan_name
        plans = self.__get_plans(context)
        if plan_name in plans:
            raise PlanTransferError(plan_name)
        plan.clear_students()
        plans.update({plan_name: plan})
        context.user_data.pop("saved_plan")
        await self._like(update)

    @admin_only
    @prevent_edited
    async def _get_owners(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Get all plan owners
        
        """
        plans = self.__get_plans(context)
        owners = "\n".join(f"{plan[0]} - {plan[1].owner}" for plan in plans.items())
        if not owners:
            raise NoPlansFoundError()
        await update.message.reply_text(owners)

    @callback_handler
    async def _get_students_callback(self, update: Update,
                                     context: ContextTypes.DEFAULT_TYPE) -> None:
        data = update.callback_query.data
        group_id = update.effective_chat.id
        plan_name = data.split(":")[1]
        plan = context.chat_data["plans"].get(plan_name, None)
        if not plan:
            raise PlanNotFoundError(plan_name)
        students = plan.students
        await context.bot.delete_message(group_id, update.effective_message.id)
        await context.bot.send_message(group_id, f"Students:\n{'\n'.join(students)}")

    @prevent_edited
    async def _get_students(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Get all students in a plan
        
        Usage: /get_students
        """
        plans = self.__get_plans(context)
        user_id = update.effective_user.id
        picker = ButtonPicker([{name: name} for name, plan in plans.items()
                               if self.__is_owner(plan, user_id)], "get_students",
                              user_id=user_id)
        if picker.is_empty:
            raise NoPlansFoundError()
        await update.message.reply_text("Choose a plan to get students from:", reply_markup=picker)

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

        if not plan:
            raise PlanNotFoundError(plan_name)

        user_id = update.effective_user.id
        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        if "new_owner" not in kwargs:
            raise InvalidValueError("new_owner")

        new_owner = str_to_i(kwargs.get("new_owner"))

        plan.owner = new_owner
        await self._like(update)
