""" Planner module for telebot. """

from typing import TYPE_CHECKING, Optional
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from dsb.types.lesson import Lesson, get_valid_day
from dsb.types.plan import Plan
from dsb.types.module import BaseModule, prevent_edited, admin_only
from dsb.types.dsb_error import DSBError
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

class NoStudentsError(DSBError):
    """ Raised when no students are found """
    def __init__(self, *args) -> None:
        super().__init__("No students found", *args)

class InvalidParameterError(DSBError):
    """ Raised when invalid parameter is provided """
    def __init__(self, parameter: str, *args) -> None:
        super().__init__(f"Please provide valid {parameter} value", *args)

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
            "join_plan": self.join_plan,
            "leave_plan": self.leave_plan,
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

    def __get_int(self, string: str) -> Optional[int]:
        if not string.isdigit():
            return None
        return int(string)

    def __is_owner(self, plan: Plan, user_id: int) -> bool:
        return user_id == plan.owner or str(user_id) in self.config["admins"]

    def create_plan(self, name: str, group_id: int, user_id: int):
        """ Create a new lesson plan """
        new_plan = Plan(user_id)
        plans = self._db.get_table("plans")
        if not all((name, group_id, new_plan)):
            raise InvalidParameterError("name")
        if plans.get_row((name, group_id)):
            raise PlanAlreadyExistsError(name)
        plans.add_row([name, group_id, new_plan])
        plans.save()

    def transfer_plan(self, plan_name: str, plan: Plan, new_group: int, force: bool) -> None:
        """ Transfer plan to another group """
        if not plan:
            raise PlanNotFoundError(plan_name)

        if not new_group:
            raise InvalidParameterError("new_group")

        existing_plan = self.get_plan(plan_name, new_group)

        if not force and existing_plan:
            raise PlanAlreadyExistsError(plan_name)

        if not existing_plan:
            self.create_plan(plan_name, new_group, new_group)

        self.update_plan(plan_name, new_group, plan)

    def get_plan(self, name: str, group_id: int) -> Plan | None:
        """ Get a lesson plan """
        plans = self._db.get_table("plans")
        row = plans.get_row((name, group_id))
        if not row:
            return None
        return row[3]

    def delete_plan(self, name: str, group_id: int, user_id: int) -> None:
        """ Delete a lesson plan """
        plan = self.get_plan(name, group_id)

        if plan is None:
            raise PlanNotFoundError(name)

        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        plans = self._db.get_table("plans")
        plans.remove_row((name, group_id))
        plans.save()

    def get_plans(self, group_id: int) -> dict[str, Plan]:
        """ Get all lesson plans """
        plans = self._db.get_table("plans")
        group_plans = plans.get_rows(check_function=lambda x: x[2] == group_id)
        return {plan[1]: plan[3] for plan in group_plans}

    def update_plan(self, name: str, group_id: int, new_plan: Plan, new_name: str = "") -> bool:
        """ Update a lesson plan """
        plans = self._db.get_table("plans")
        plan = plans.get_row((name, group_id))
        if not plan:
            return False
        if new_name:
            plan[1] = new_name
        plan[3] = new_plan
        plans.replace_row((name, group_id), plan)
        plans.save()
        return True

    def get_status(self, group_id: int) -> tuple[list[tuple[str, str]]]:
        """ Return complete status of all students in a group """
        plans = self.get_plans(group_id)
        if not plans:
            return [], []
        free_students = []
        busy_students = []
        for plan in plans.values():
            if plan.is_free():
                next_lesson = plan.next_lesson
                if not next_lesson:
                    time_diff = "No lessons left"
                else:
                    diff = next_lesson.time_until.total_seconds()
                    time_diff = f"{int(diff // 3600)}h {int(diff//60 % 60):02}min"
                for student in plan.students:
                    free_students.append((student, time_diff))
            else:
                current_lesson = plan.current_lesson
                diff = current_lesson.time_left.total_seconds()
                lesson_info = f"{current_lesson.subject} | {current_lesson.type}\n"
                time_diff = f"{int(diff // 3600)}h {int(diff//60 % 60):02}min"
                for student in plan.students:
                    busy_students.append((student, lesson_info + time_diff))
        return free_students, busy_students

    async def __get_plan_from_update(self, update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> tuple[str, Plan, dict]:
        """ Returns plan name, plan object and kwargs """
        if not context.args:
            # await self._reply_t(update, "Use /help command_name to learn how to use this command")
            return None, None, None

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        plan = self.get_plan(plan_name, group_id)

        return plan_name, plan, kwargs

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

        plan_name, plan, kwargs = await self.__get_plan_from_update(update, context)
        new_group = self.__get_int(kwargs.get("new_group", ""))

        self.transfer_plan(plan_name, plan, new_group, kwargs.get("force", False))

        await self._affirm(update)

    @prevent_edited
    async def _create_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Create a new lesson plan """
        plan_name, _, _ = await self.__get_plan_from_update(update, context)

        group_id = update.effective_chat.id

        self.create_plan(plan_name, group_id, update.effective_user.id)

        await self._affirm(update)

    @prevent_edited
    async def _delete_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Delete a lesson plan """
        plan_name, _, _ = await self.__get_plan_from_update(update, context)

        group_id = update.effective_chat.id

        self.delete_plan(plan_name, group_id, update.effective_user.id)

        await self._affirm(update)

    @prevent_edited
    async def _edit_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Editing a plan name """
        group_id = update.effective_chat.id

        plan_name, plan, kwargs = await self.__get_plan_from_update(update, context)

        if plan is None:
            raise PlanNotFoundError(plan_name)

        user_id = update.effective_user.id

        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        self.update_plan(plan_name, group_id, plan, kwargs.get("new_name"))
        await self._affirm(update)

    @admin_only
    @prevent_edited
    async def _delete_all(self, update: Update, _) -> None:
        """ Delete all lesson plans """
        group_id = update.effective_chat.id
        plans = self.get_plans(group_id)
        user_id = update.effective_user.id
        for plan in plans:
            try:
                self.delete_plan(plan, group_id, user_id)
            except DSBError:
                continue
        await self._affirm(update)

    @admin_only
    @prevent_edited
    async def _get_owners(self, update: Update, _) -> None:
        """ Get all plan owners """
        group_id = update.effective_chat.id
        plans = self.get_plans(group_id)
        owners = "\n".join(f"{plan[0]} - {plan[1].owner}" for plan in plans.items())
        if not owners:
            await update.message.reply_text("No plans found")
            return
        await update.message.reply_text(owners)

    @prevent_edited
    async def _transfer_plan_ownership(self, update: Update,
                                       context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Transfer plan ownership """
        plan_name, plan, kwargs = await self.__get_plan_from_update(update, context)

        group_id = update.effective_chat.id

        if not plan:
            raise PlanNotFoundError(plan_name)

        user_id = update.effective_user.id
        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        if "new_owner" not in kwargs:
            raise InvalidParameterError("new_owner")

        new_owner = int(kwargs.get("new_owner"))

        plan.owner = new_owner
        self.update_plan(plan_name, group_id, plan)
        await self._affirm(update)

    @prevent_edited
    async def _get_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Get a lesson plan """
        plan = None
        plan_name = None
        if not context.args:
            group_id = update.effective_chat.id
            plans = self._db.get_table("plans")
            username = update.message.from_user.username
            row = plans.get_row(check_function=lambda x: x[2] == group_id and
                                 username in x[3].students)
            if not row:
                await update.message.reply_text("You do not belong to a plan." + \
                                            "Please use /join_plan command")
                return
            plan: Plan = row[3]
            plan_name = row[1]

        if not plan:
            plan_name, plan, _ = await self.__get_plan_from_update(update, context)

        if plan:
            if plan.is_empty():
                raise PlanEmptyError()
            plan_image = plan.to_image()
            await update.message.reply_photo(plan_image)
        else:
            raise PlanNotFoundError(plan_name)

    @prevent_edited
    async def _get_plans(self, update: Update, _) -> None:
        """ Get all lesson plans """
        group_id = update.effective_chat.id
        plans = self.get_plans(group_id)
        plans_str = ""
        for i, plan in enumerate(plans.items()):
            students = plan[1].students
            if not students:
                students = ["No students in the plan"]
            plans_str += f"{i+1}. {plan[0]}\n{'\n'.join(students)}\n"
        if plans:
            await update.message.reply_text(plans_str)
        else:
            await update.message.reply_text("No plans found")

    @prevent_edited
    async def _add_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Add a lesson to a plan """
        plan_name, plan, kwargs = await self.__get_plan_from_update(update, context)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        try:
            new_lesson = Lesson(kwargs)
        except KeyError as key:
            raise InvalidParameterError(key) from key

        group_id = update.effective_chat.id

        plan.add_lesson(new_lesson.day - 1, new_lesson)
        self.update_plan(plan_name, group_id, plan)
        await self._affirm(update)

    @prevent_edited
    async def _remove_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Remove a lesson from a plan """
        plan_name, plan, kwargs = await self.__get_plan_from_update(update, context)

        group_id = update.effective_chat.id

        if not plan:
            raise PlanNotFoundError(plan_name)

        user_id = update.effective_user.id
        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        if "idx" not in kwargs or not kwargs.get("idx").isdigit():
            raise InvalidParameterError("idx")

        idx = int(kwargs.get("idx"))
        day = get_valid_day(kwargs.get("day", ""))

        if not day:
            raise InvalidParameterError("day")

        try:
            plan.remove_lesson_by_index(int(day) - 1, idx)
            self.update_plan(plan_name, group_id, plan)
            await self._affirm(update)
        except IndexError:
            await update.message.reply_text("Lesson not found")

    @prevent_edited
    async def _edit_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Edit a lesson in a plan """
        plan_name, plan, kwargs = await self.__get_plan_from_update(update, context)

        if not plan:
            raise PlanNotFoundError(plan_name)

        user_id = update.effective_user.id
        if plan.owner != user_id and not str(user_id) in self.config["admins"]:
            raise PlanOwnershipError()

        if "idx" not in kwargs or not kwargs.get("idx").isdigit():
            raise InvalidParameterError("idx")

        idx = int(kwargs.get("idx"))
        day = get_valid_day(kwargs.get("day", ""))
        new_day = get_valid_day(kwargs.get("new_day", ""))

        if not day:
            raise InvalidParameterError("day")

        lessons = plan.get_day(day - 1)
        if not lessons:
            await update.message.reply_text("No lessons for this day")
            return

        try:
            lesson = lessons[idx]
        except IndexError:
            await update.message.reply_text("Lesson not found")
            return

        if new_day:
            kwargs["day"] = kwargs["new_day"]

        lesson_data = lesson.to_dict()
        lesson_data.update(kwargs)

        try:
            new_lesson = Lesson(lesson_data)
        except ValueError as e:
            await update.message.reply_text(str(e))
            return

        plan.remove_lesson_by_index(day - 1, idx)
        plan.add_lesson(new_day - 1 if new_day else day - 1, new_lesson)
        self.update_plan(plan_name, update.effective_chat.id, plan)
        await self._affirm(update)

    @prevent_edited
    async def _clear_day(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Clear all lessons for a day """
        plan_name, plan, kwargs = await self.__get_plan_from_update(update, context)

        group_id = update.effective_chat.id

        if not plan:
            raise PlanNotFoundError(plan_name)

        user_id = update.effective_user.id
        if not self.__is_owner(plan, user_id):
            raise PlanOwnershipError()

        args, kwargs = self._get_args(context)
        if "day" in kwargs:
            day = kwargs.get("day")
        else:
            day = " ".join(args)

        day = get_valid_day(day)

        if not day:
            raise InvalidParameterError("day")

        plan.clear_day(day - 1)
        self.update_plan(plan_name, group_id, plan)
        await self._affirm(update)

    @prevent_edited
    async def _clear_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Clear all lessons for a plan """
        plan_name, plan, _ = await self.__get_plan_from_update(update, context)

        group_id = update.effective_chat.id

        if not plan:
            raise PlanNotFoundError(plan_name)

        plan.clear_all()
        self.update_plan(plan_name, group_id, plan)
        await self._affirm(update)

    @prevent_edited
    async def _get_room(self, update: Update, _) -> None:
        plans = self.get_plans(update.effective_chat.id)

        if not plans:
            await update.message.reply_text("No plans found")
            return

        group_id = update.effective_chat.id
        plans = self.get_plans(group_id)
        for plan in plans.values():
            if update.message.from_user.username in plan.students:
                lesson = plan.next_lesson
                if not lesson:
                    await update.message.reply_text("You don't have any lesson next")
                    return
                await update.message.reply_text(f"You have your next lesson in {lesson.room}")
                return
        await update.message.reply_text("You do not belong to a plan." + \
                                        "Please use /join_plan command")

    @prevent_edited
    async def _status(self, update: Update, _) -> None:
        plans = self.get_plans(update.effective_chat.id)

        if not plans:
            await update.message.reply_text("No plans found")
            return

        today = datetime.today().weekday()

        if today > 4:
            await update.message.reply_text("No lessons tooday")
            return

        free_students, busy_students = self.get_status(update.effective_chat.id)

        student_list = "Free right now:\n" + \
            "\n".join(f"{student} - {text}" for student, text in free_students) + \
            "\n\nBusy right now: \n" + \
            "\n".join(f"{student} - {text}" for student, text in busy_students)

        await update.message.reply_text(student_list)

    @prevent_edited
    async def _get_students(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Get all students in a plan """
        plan_name, plan, _ = await self.__get_plan_from_update(update, context)

        if not plan:
            raise PlanNotFoundError(plan_name)

        student_list = "\n".join(f"{i+1}. {student}" for i, student in enumerate(plan.students))
        if not student_list:
            raise NoStudentsError()
        await update.message.reply_text(f"Students:\n{student_list}")

    @prevent_edited
    async def join_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Join a lesson plan """
        plan_name, plan, _ = await self.__get_plan_from_update(update, context)

        group_id = update.effective_chat.id

        if not plan:
            raise PlanNotFoundError(plan_name)

        plans = self.get_plans(group_id)
        for name, current_plan in plans.items():
            if update.effective_user.username in current_plan.students:
                current_plan.remove_student(update.effective_user.username)
                self.update_plan(name, group_id, current_plan)

        try:
            plan.add_student(update.effective_user.username)
        except ValueError as e:
            await update.message.reply_text(str(e))
            return
        self.update_plan(plan_name, group_id, plan)
        await self._affirm(update)

    @prevent_edited
    async def leave_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Leave a lesson plan """
        plan_name, plan, _ = await self.__get_plan_from_update(update, context)

        group_id = update.effective_chat.id

        if not plan:
            raise PlanNotFoundError(plan_name)

        try:
            plan.remove_student(update.effective_user.username)
        except ValueError:
            await update.message.reply_text("You are not in the plan")
            return
        self.update_plan(plan_name, group_id, plan)
        await self._affirm(update)

    def prepare(self):
        self._db.add_table("plans", [("name", str, True),
                                     ("group_id", int, True),
                                     ("plan", Plan, False)], True)
        return super().prepare()
