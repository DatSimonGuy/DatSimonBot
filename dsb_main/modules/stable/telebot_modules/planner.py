""" Planner module for telebot. """

from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from dsb_main.modules.stable.planning import Planning
from dsb_main.modules.stable.types.lesson import Lesson
from .base.base_module import BaseModule, prevent_edited

class Planner(BaseModule):
    """ Planner module """
    def __init__(self, ptb, telebot_module) -> None:
        super().__init__(ptb, telebot_module)
        self._planning_module: Planning = None
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
            "who_is_free": self._who_is_free,
            "join_plan": self.join_plan,
            "leave_plan": self.leave_plan,
            "get_students": self._get_students
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
            "who_is_free": "Find out who is free at a given time",
            "join_plan": "Join a lesson plan",
            "leave_plan": "Leave a lesson plan",
            "get_students": "Get all students in a plan"
        }

    @prevent_edited
    async def _create_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Create a new lesson plan """
        if not context.args:
            await update.message.reply_text("Please provide a name for the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id

        if self._planning_module.get_plan(plan_name, group_id):
            await update.message.reply_text("A plan with that name already exists")
            return

        if self._planning_module.create_plan(plan_name, group_id):
            await update.message.set_reaction("👍")
        else:
            await update.message.reply_text("An error occurred")

    @prevent_edited
    async def _delete_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Delete a lesson plan """
        if not context.args:
            await update.message.reply_text("Please provide the name of the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        if self._planning_module.delete_plan(plan_name, group_id):
            await update.message.set_reaction("👍")
        else:
            await update.message.reply_text("An error occurred")

    @prevent_edited
    async def _edit_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Editing a plan name """
        if not context.args:
            await update.message.reply_text("Please provide the name of the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        plan = self._planning_module.get_plan(plan_name, group_id)

        if plan is None:
            await update.message.reply_text("Plan not found")
            return

        if self._planning_module.get_plan(kwargs.get("new_name"), group_id):
            await update.message.reply_text("A plan with that name already exists")

        self._planning_module.update_plan(plan_name, group_id, plan, kwargs.get("new_name"))
        await update.message.set_reaction("👍")

    @prevent_edited
    async def _delete_all(self, update: Update, _) -> None:
        """ Delete all lesson plans """
        group_id = update.effective_chat.id
        plan_names = self._planning_module.get_plans(group_id)
        for plan in plan_names:
            if not self._planning_module.delete_plan(plan, group_id):
                await update.message.reply_text("An error occurred")
                return
        await update.message.set_reaction("👍")

    @prevent_edited
    async def _get_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Get a lesson plan """
        if not context.args:
            await update.message.reply_text("Please provide a name for the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        plan = self._planning_module.get_plan(plan_name, group_id)
        if plan:
            if plan.is_empty():
                await update.message.reply_text("Plan is empty")
                return
            plan_image = plan.to_image()
            await update.message.reply_photo(plan_image)
        else:
            await update.message.reply_text("Plan not found")

    @prevent_edited
    async def _get_plans(self, update: Update, _) -> None:
        """ Get all lesson plans """
        group_id = update.effective_chat.id
        plans = self._planning_module.get_plans(group_id)
        plans_str = ""
        for i, plan in enumerate(plans):
            plans_str += f"{i+1}. {plan}\n"
        if plans:
            await update.message.reply_text(plans_str)
        else:
            await update.message.reply_text("No plans found")

    @prevent_edited
    async def _add_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Add a lesson to a plan """
        args, kwargs = self._get_args(context)
        if not args and not kwargs.get("plan", None):
            await update.message.reply_text("Please provide a name for the plan")
            return
        try:
            new_lesson = Lesson(kwargs["subject"], kwargs["teacher"], kwargs["room"],
                                datetime.strptime(kwargs["start"], "%H:%M").time(),
                                datetime.strptime(kwargs["end"], "%H:%M").time(), kwargs["day"],
                                kwargs["type"])
        except KeyError as key:
            await update.message.reply_text(f"Missing argument: {key}")
            return

        group_id = update.effective_chat.id
        plan_name = " ".join(args) if args else kwargs["plan"]

        plan = self._planning_module.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        days = {
            "monday": 1,
            "tuesday": 2,
            "wednesday": 3,
            "thursday": 4,
            "friday": 5
        }

        try:
            if new_lesson.day not in "12345":
                new_lesson.day = days[new_lesson.day.lower()]
        except KeyError:
            await update.message.reply_text("Invalid day")
            return

        plan.add_lesson(int(new_lesson.day) - 1, new_lesson)
        self._planning_module.update_plan(plan_name, group_id, plan)
        await update.message.set_reaction("👍")

    @prevent_edited
    async def _remove_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Remove a lesson from a plan """
        if not context.args:
            await update.message.reply_text("Please provide a name for the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        plan = self._planning_module.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        args, kwargs = self._get_args(context)
        if "idx" in kwargs:
            idx = int(kwargs.get("idx"))
        else:
            try:
                idx = int(" ".join(args))
            except ValueError:
                await update.message.reply_text("Invalid index")
                return

        days = {
            "monday": 1,
            "tuesday": 2,
            "wednesday": 3,
            "thursday": 4,
            "friday": 5
        }

        if "day" not in kwargs:
            await update.message.reply_text("Please provide a day")
            return

        day = kwargs.get("day")

        try:
            if day not in "12345":
                day = days[kwargs["day"].lower()]
        except KeyError:
            await update.message.reply_text("Invalid day")
            return

        try:
            plan.remove_lesson_by_index(int(day) - 1, idx)
            self._planning_module.update_plan(plan_name, group_id, plan)
            await update.message.set_reaction("👍")
        except IndexError:
            await update.message.reply_text("Lesson not found")

    @prevent_edited
    async def _edit_lesson(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Edit a lesson in a plan """
        if not context.args:
            await update.message.reply_text("Please provide a name for the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        plan = self._planning_module.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        args, kwargs = self._get_args(context)
        if "idx" in kwargs:
            idx = int(kwargs.get("idx"))
        else:
            try:
                idx = int(" ".join(args))
            except ValueError:
                await update.message.reply_text("Invalid index")
                return

        days = {
            "monday": 1,
            "tuesday": 2,
            "wednesday": 3,
            "thursday": 4,
            "friday": 5
        }

        if "day" not in kwargs:
            await update.message.reply_text("Please provide a day")
            return

        try:
            if kwargs["day"] not in "12345":
                day = days[kwargs["day"].lower()]
            else:
                day = int(kwargs["day"])
        except KeyError:
            await update.message.reply_text("Invalid day")
            return

        lesson = plan.get_day(int(day) - 1)[idx]
        lesson.update(kwargs)

        try:
            plan.remove_lesson_by_index(int(day) - 1, idx)
            plan.add_lesson(int(day) - 1, lesson)
            self._planning_module.update_plan(plan_name, group_id, plan)
            await update.message.set_reaction("👍")
        except IndexError:
            await update.message.reply_text("Lesson not found")

    @prevent_edited
    async def _clear_day(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Clear all lessons for a day """
        if not context.args:
            await update.message.reply_text("Please provide a name for the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        plan = self._planning_module.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        args, kwargs = self._get_args(context)
        if "day" in kwargs:
            day = kwargs.get("day")
        else:
            day = " ".join(args)

        days = {
            "monday": 1,
            "tuesday": 2,
            "wednesday": 3,
            "thursday": 4,
            "friday": 5
        }

        try:
            if day not in "12345":
                day = days[day.lower()]
        except KeyError:
            await update.message.reply_text("Invalid day")
            return

        plan.clear_day(int(day) - 1)
        self._planning_module.update_plan(plan_name, group_id, plan)
        await update.message.set_reaction("👍")

    @prevent_edited
    async def _clear_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Clear all lessons for a plan """
        if not context.args:
            await update.message.reply_text("Please provide a name for the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        plan = self._planning_module.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        plan.clear_all()
        self._planning_module.update_plan(plan_name, group_id, plan)
        await update.message.set_reaction("👍")

    @prevent_edited
    async def _who_is_free(self, update: Update, _) -> None:
        """ Find out who is free at a given time """
        plans = self._planning_module.get_plans(update.effective_chat.id)

        if not plans:
            await update.message.reply_text("No plans found")
            return

        today = datetime.today().weekday()

        if today > 4:
            await update.message.reply_text("No lessons today")
            return

        free_students = self._planning_module.who_is_free(update.effective_chat.id)

        student_list = "\n".join(f"{student} - {text}" for student, text in free_students)
        if not student_list:
            await update.message.reply_text("No students are free")
            return
        await update.message.reply_text(f"Free students:\n{student_list}")

    @prevent_edited
    async def _get_students(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Get all students in a plan """
        if not context.args:
            await update.message.reply_text("Please provide a name for the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        plan = self._planning_module.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        student_list = "\n".join(f"{i+1}. {student}" for i, student in enumerate(plan.students))
        if not student_list:
            await update.message.reply_text("No students in the plan")
            return
        await update.message.reply_text(f"Students:\n{student_list}")

    @prevent_edited
    async def join_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Join a lesson plan """
        if not context.args:
            await update.message.reply_text("Please provide a name for the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        plan = self._planning_module.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        plan.add_student(update.effective_user.username)
        self._planning_module.update_plan(plan_name, group_id, plan)
        await update.message.set_reaction("👍")

    @prevent_edited
    async def leave_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Leave a lesson plan """
        if not context.args:
            await update.message.reply_text("Please provide a name for the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        plan = self._planning_module.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        plan.remove_student(update.effective_user.username)
        self._planning_module.update_plan(plan_name, group_id, plan)
        await update.message.set_reaction("👍")

    def prepare(self) -> bool:
        """ Prepare the module """
        self._planning_module = self._telebot_module.get_dsb_module("Planning")
        if not self._planning_module:
            self._telebot_module.log("ERROR", "Planning module not found")
            return False
        return True
