""" Planner module for telebot. """

from typing import TYPE_CHECKING
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from dsb.types.lesson import Lesson
from dsb.types.plan import Plan
from dsb.types.module import BaseModule, prevent_edited, admin_only
if TYPE_CHECKING:
    from dsb.dsb import DSB

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
            "who_is_free": self._who_is_free,
            "join_plan": self.join_plan,
            "leave_plan": self.leave_plan,
            "get_students": self._get_students,
            "transfer_plan": self._transfer_plan
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
            "get_students": "Get all students in a plan",
            "transfer_plan": "Transfer a plan to another group"
        }

    def create_plan(self, name: str, group_id: int, user_id: int) -> bool:
        """ Create a new lesson plan """
        new_plan = Plan(name, owner=user_id)
        return self._db.save(new_plan, f"{group_id}/plans", name)

    def get_plan(self, name: str, group_id: int) -> Plan | None:
        """ Get a lesson plan """
        return self._db.load(f"{group_id}/plans", name)

    def delete_plan(self, name: str, group_id: int) -> bool:
        """ Delete a lesson plan """
        return self._db.delete(f"{group_id}/plans", name)

    def get_plans(self, group_id: int) -> dict[str, Plan]:
        """ Get all lesson plans """
        plan_list = self._db.list_all(f"{group_id}/plans")
        plan_list = [plan.split(".")[0] for plan in plan_list]
        plans = {}
        for plan_name in plan_list:
            plans[plan_name] = self.get_plan(plan_name, group_id)
        return dict(sorted(plans.items()))

    def update_plan(self, name: str, group_id: int, new_plan: Plan, new_name: str = "") -> bool:
        """ Update a lesson plan """
        if new_name:
            self._db.delete(f"{group_id}/plans", name)
            return self._db.save(new_plan, f"{group_id}/plans", new_name)
        return self._db.save(new_plan, f"{group_id}/plans", name)

    def who_is_free(self, group_id: int) -> list[tuple[str, str]]:
        """ Get a list of students who are free at a given time and seconds to the next lesson """
        plans = self.get_plans(group_id)
        if not plans:
            return []
        free_students = []
        for plan in plans.values():
            if plan.is_free():
                next_lesson = plan.next_lesson
                if not next_lesson:
                    time_diff = "No lessons left"
                else:
                    diff = next_lesson.time_until.total_seconds()
                    time_diff = f"{int(diff // 3600)}h {int((diff % 3600) // 60):02}min"
                for student in plan.students:
                    free_students.append((student, time_diff))
        return free_students

    @prevent_edited
    async def _transfer_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Transfer a plan to another group """
        if not context.args:
            await update.message.reply_text("Please provide a name for the plan")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        group_id = update.effective_chat.id
        plan = self.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        if "new_group" not in kwargs:
            await update.message.reply_text("Please provide a new group id")
            return

        new_group = int(kwargs.get("new_group"))

        if not kwargs.get("ignore_existing", False) and \
            self.get_plan(plan_name, new_group):
            await update.message.reply_text("A plan with that name already exists")
            return

        self.create_plan(plan_name, new_group, update.effective_user.id)
        self.update_plan(plan_name, new_group, plan)
        await update.message.set_reaction("👍")

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

        if plan_name.isdigit():
            await update.message.reply_text("Plan name cannot be a number")
            return

        group_id = update.effective_chat.id

        if self.get_plan(plan_name, group_id):
            await update.message.reply_text("A plan with that name already exists")
            return

        if self.create_plan(plan_name, group_id, update.effective_user.id):
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
        plan = self.get_plan(plan_name, group_id)

        if plan is None:
            await update.message.reply_text(f"There is no plan with name {plan_name}")
            return

        user_id = update.effective_chat.id
        if user_id != plan.owner and user_id not in self.config["admins"]:
            await update.message.reply_text("This plan does not belong to you")
            return

        if self.delete_plan(plan_name, group_id):
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
        plan = self.get_plan(plan_name, group_id)

        if plan is None:
            await update.message.reply_text("Plan not found")
            return

        user_id = update.effective_user.id
        if plan.owner != user_id and user_id not in self.config["admins"]:
            await update.message.reply_text("This is not your plan")

        if self.get_plan(kwargs.get("new_name"), group_id):
            await update.message.reply_text("A plan with that name already exists")

        self.update_plan(plan_name, group_id, plan, kwargs.get("new_name"))
        await update.message.set_reaction("👍")

    @admin_only
    @prevent_edited
    async def _delete_all(self, update: Update, _) -> None:
        """ Delete all lesson plans """
        group_id = update.effective_chat.id
        plans = self.get_plans(group_id)
        for plan in plans:
            if not self.delete_plan(plan, group_id):
                await update.message.reply_text("An error occurred")
                return
        await update.message.set_reaction("👍")

    @prevent_edited
    async def _get_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Get a lesson plan """
        if not context.args:
            group_id = update.effective_chat.id
            plans = self.get_plans(group_id)
            for plan_name, plan in plans.items():
                if update.message.from_user.username in plan.students:
                    plan_image = plan.to_image()
                    await update.message.reply_photo(plan_image)
                    return
            await update.message.reply_text("You do not belong to a plan." + \
                                            "Please use /join_plan command")
            return

        args, kwargs = self._get_args(context)
        if "name" in kwargs:
            plan_name = kwargs.get("name")
        else:
            plan_name = " ".join(args)

        if plan_name.isdigit():
            plans = self.get_plans(update.effective_chat.id)
            if int(plan_name) <= len(plans):
                plan_name = list(plans.keys())[int(plan_name) - 1]
            else:
                await update.message.reply_text("Plan not found")
                return

        group_id = update.effective_chat.id
        plan = self.get_plan(plan_name, group_id)
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
        args, kwargs = self._get_args(context)
        if not args and not kwargs.get("plan", None):
            await update.message.reply_text("Please provide a name for the plan")
            return
        try:
            if len(kwargs["subject"].split()) > 2:
                await update.message.reply_text("Subject must be one or two words")
                return
            new_lesson = Lesson(kwargs["subject"], kwargs["teacher"], kwargs["room"],
                                datetime.strptime(kwargs["start"], "%H:%M").time(),
                                datetime.strptime(kwargs["end"], "%H:%M").time(), kwargs["day"],
                                kwargs["type"])
        except KeyError as key:
            await update.message.reply_text(f"Missing argument: {key}")
            return

        group_id = update.effective_chat.id
        plan_name = " ".join(args) if args else kwargs["plan"]

        plan = self.get_plan(plan_name, group_id)

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
                day = days[new_lesson.day.lower()]
            else:
                day = int(new_lesson.day)
        except KeyError:
            await update.message.reply_text("Invalid day")
            return

        plan.add_lesson(day - 1, new_lesson)
        self.update_plan(plan_name, group_id, plan)
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
        plan = self.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        user_id = update.effective_user.id
        if plan.owner != user_id and not user_id in self.config["admins"]:
            await update.message.reply_text("This plan does not belong to you")
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
            self.update_plan(plan_name, group_id, plan)
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
        plan = self.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        user_id = update.effective_user.id
        if plan.owner != user_id and not user_id in self.config["admins"]:
            await update.message.reply_text("This plan does not belong to you")
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
            day = days.get(kwargs["day"].lower(), int(kwargs["day"]))
            new_day = days.get(kwargs.get("new_day", "").lower(),
                               int(kwargs["new_day"])) if kwargs.get("new_day") else None
        except KeyError:
            await update.message.reply_text("Invalid day")
            return

        lesson = plan.get_day(day - 1)[idx]

        if len(kwargs.get("subject", "").split()) > 2:
            await update.message.reply_text("Subject must be one or two words")
            return

        lesson.update(kwargs)

        try:
            plan.remove_lesson_by_index(day - 1, idx)
            plan.add_lesson(new_day - 1 if new_day else day - 1, lesson)
            self.update_plan(plan_name, group_id, plan)
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
        plan = self.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        user_id = update.effective_user.id
        if plan.owner != user_id and not user_id in self.config["admins"]:
            await update.message.reply_text("This plan does not belong to you")
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
        self.update_plan(plan_name, group_id, plan)
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
        plan = self.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        plan.clear_all()
        self.update_plan(plan_name, group_id, plan)
        await update.message.set_reaction("👍")

    @prevent_edited
    async def _who_is_free(self, update: Update, _) -> None:
        """ Find out who is free at a given time """
        plans = self.get_plans(update.effective_chat.id)

        if not plans:
            await update.message.reply_text("No plans found")
            return

        today = datetime.today().weekday()

        if today > 4:
            await update.message.reply_text("No lessons today")
            return

        free_students = self.who_is_free(update.effective_chat.id)

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
        plan = self.get_plan(plan_name, group_id)

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
        plan = self.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        plan.add_student(update.effective_user.username)
        self.update_plan(plan_name, group_id, plan)
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
        plan = self.get_plan(plan_name, group_id)

        if not plan:
            await update.message.reply_text(f"Plan {plan_name} not found")
            return

        plan.remove_student(update.effective_user.username)
        self.update_plan(plan_name, group_id, plan)
        await update.message.set_reaction("👍")
