from utils.types import lesson
import telebot.async_telebot as async_telebot
from telebot.types import Message, ReactionTypeEmoji
from ..types.databases.plansDatabase import PlansDatabase
from .dsbModule import DsbModule

class PlaningModule(DsbModule):
    def __init__(self, bot: async_telebot.AsyncTeleBot) -> None:
        super().__init__(bot)
        self._database: PlansDatabase = PlansDatabase("data/plans")
        self._load() # load plans from file if they already exist
    
    def _add_handlers(self, bot: async_telebot.AsyncTeleBot) -> None:
        bot.register_message_handler(self._new_plan, commands=["new_plan"], pass_bot=True)
        bot.register_message_handler(self._remove_plan, commands=["remove_plan"], pass_bot=True)
        bot.register_message_handler(self._get_plan, commands=["get_plan"], pass_bot=True)
        bot.register_message_handler(self._join_plan, commands=["join_plan"], pass_bot=True)
        bot.register_message_handler(self._leave_plan, commands=["leave_plan"], pass_bot=True)
        bot.register_message_handler(self._add_lesson, commands=["add_lesson"], pass_bot=True)
        bot.register_message_handler(self._remove_lesson, commands=["remove_lesson"], pass_bot=True)
        bot.register_message_handler(self._edit_lesson, commands=["edit_lesson"], pass_bot=True)
        bot.register_message_handler(self._move_lesson, commands=["move_lesson"], pass_bot=True)

    async def _new_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ creates a new plan with the specified name

        Args:
            message (Message): message with the plan name
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided or the plan already exists

        """
        try:
            arguments = self._parse_input(message, "plan_name")

            if "plan_name" not in arguments:
                raise ValueError("You need to specify a name for the plan.")

            self._database.new_plan(message.chat.id, arguments["plan_name"])
            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def _remove_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ removes a plan with the specified name

        Args:
            message (Message): message with the plan name
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided or the plan does not exist

        """
        try:
            arguments = self._parse_input(message, "plan_name")
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a name for the plan.")
            
            self._database.remove_plan(message.chat.id, arguments["plan_name"])
            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return

    async def _get_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ returns the plan with the specified name

        Args:
            message (Message): message with the plan name
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided or the plan does not exist

        """
        try:
            arguments = self._parse_input(message, "plan_name")
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a name for the plan.")
            
            retarded = "retarded" in arguments
            
            plan = self._database.get_plan(message.chat.id, arguments["plan_name"])
            
            if not retarded:
                response = str(plan)
            else:
                response = plan.retarded_str()

            await bot.send_message(message.chat.id, response)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def _join_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ allows user to join the plan with the specified name

        Args:
            message (Message): message with the plan name
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self._parse_input(message, "plan_name")

            if "plan_name" not in arguments:
                raise ValueError("You need to specify a name for the plan you want to join.")

            self._database.add_person(message.chat.id, arguments["plan_name"], message.from_user)

            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def _leave_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ allows user to leave the plan with the specified name

        Args:
            message (Message): message with the plan name
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self._parse_input(message, "plan_name")

            if "plan_name" not in arguments:
                raise ValueError("You need to specify a name for the plan you want to leave.")

            self._database.remove_person(message.chat.id, arguments["plan_name"], message.from_user.id)

            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def _add_lesson(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ adds a lesson to the plan with the specified name

        Args:
            message (Message): message with the lesson arguments
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self._parse_input(message, "plan_name")
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a plan for the lesson.")
            
            new_lesson = lesson.Lesson(arguments)
            
            self._database.add_lesson(message.chat.id, arguments["plan_name"], arguments.get("day", 0), new_lesson)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return

    async def _remove_lesson(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ removes a lesson from the plan with the specified name

        Args:
            message (Message): message with the lesson arguments
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self._parse_input(message, "plan_name")
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a plan for the lesson.")
            
            self._database.remove_lesson(message.chat.id, arguments["plan_name"], arguments.get("day", 0), arguments.get("idx", 0))
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def _edit_lesson(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ edits a lesson in the plan with the specified name

        Args:
            message (Message): message with the lesson arguments
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self._parse_input(message, "plan_name")
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a plan for the lesson.")

            lesson_to_edit = self._database.get_lesson(message.chat.id, arguments["plan_name"], arguments.get("day", 0), arguments.get("idx", 0))
            
            lesson_to_edit.read_args(arguments)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def _move_lesson(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ moves a lesson in the plan with the specified name

        Args:
            message (Message): message with the lesson arguments
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self._parse_input(message, "plan_name")
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a plan for the lesson.")
            
            lesson = self._database.get_lesson(message.chat.id, arguments["plan_name"], arguments.get("from-day", 0), arguments.get("from-idx", 0))
            self._database.remove_lesson(message.chat.id, arguments["plan_name"], arguments.get("from-day", 0), arguments.get("from-idx", 0))
            self._database.add_lesson(message.chat.id, arguments["plan_name"], arguments.get("to-day", 0), lesson)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    