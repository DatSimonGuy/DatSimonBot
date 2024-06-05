from utils.types import lesson
import telebot.async_telebot as async_telebot
from telebot.types import Message, ReactionTypeEmoji
import datetime
from .types import database

class PlaningModule:
    def __init__(self, bot: async_telebot.AsyncTeleBot) -> None:
        self._database: database.Database = database.Database("plans")
        self.load() # load plans from file if they already exist
        self.add_handlers(bot)
    
    def add_handlers(self, bot: async_telebot.AsyncTeleBot) -> None:
        bot.register_message_handler(self.new_plan, commands=["new_plan"], pass_bot=True)
        bot.register_message_handler(self.remove_plan, commands=["remove_plan"], pass_bot=True)
        bot.register_message_handler(self.get_plan, commands=["get_plan"], pass_bot=True)
        bot.register_message_handler(self.join_plan, commands=["join_plan"], pass_bot=True)
        bot.register_message_handler(self.leave_plan, commands=["leave_plan"], pass_bot=True)
        bot.register_message_handler(self.add_lesson, commands=["add_lesson"], pass_bot=True)
        bot.register_message_handler(self.remove_lesson, commands=["remove_lesson"], pass_bot=True)
        bot.register_message_handler(self.edit_lesson, commands=["edit_lesson"], pass_bot=True)
        bot.register_message_handler(self.move_lesson, commands=["move_lesson"], pass_bot=True)

    async def confirm(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ will react to the message with a thumbs up emoji to confirm the action

        Args:
            message (Message): message to react to
            bot (async_telebot.AsyncTeleBot): bot to react with

        """
        await bot.set_message_reaction(message.chat.id, message.message_id, [ReactionTypeEmoji("👍")])

    def parse_input(self, message: Message) -> dict[str, str]:
        """ parses the input message and returns a dictionary with the arguments and their values

        Args:
            message (Message): message to parse

        Raises:
            ValueError: if no arguments are provided

        Returns:
            dict[str, str]: dictionary with the arguments and their values

        """
        arguments = message.text.split()[1:]

        if len(arguments) == 0:
            raise ValueError("No arguments provided.")

        last_arg_name = "plan_name"
        parsed = {}
        
        for arg in arguments:
            if arg.startswith("—"):
                last_arg_name = arg.split("—")[1]
                parsed[last_arg_name] = ""
            else:
                if last_arg_name not in parsed or parsed[last_arg_name] == "":
                    parsed[last_arg_name] = arg
                else:
                    parsed[last_arg_name] += " " + arg
        
        return parsed

    async def new_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ creates a new plan with the specified name

        Args:
            message (Message): message with the plan name
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided or the plan already exists

        """
        try:
            arguments = self.parse_input(message)

            if "plan_name" not in arguments:
                raise ValueError("You need to specify a name for the plan.")

            self._database.new_plan(message.chat.id, arguments["plan_name"])
            await self.confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def remove_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ removes a plan with the specified name

        Args:
            message (Message): message with the plan name
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided or the plan does not exist

        """
        try:
            arguments = self.parse_input(message)
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a name for the plan.")
            
            self._database.remove_plan(message.chat.id, arguments["plan_name"])
            await self.confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return

    async def get_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ returns the plan with the specified name

        Args:
            message (Message): message with the plan name
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided or the plan does not exist

        """
        try:
            arguments = self.parse_input(message)
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a name for the plan.")
            
            plan = self._database.get_plan(message.chat.id, arguments["plan_name"])
            response = str(plan)

            await bot.send_message(message.chat.id, response)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def join_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ allows user to join the plan with the specified name

        Args:
            message (Message): message with the plan name
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self.parse_input(message)

            if "plan_name" not in arguments:
                raise ValueError("You need to specify a name for the plan you want to join.")

            self._database.add_person(message.chat.id, arguments["plan_name"], message.from_user)

            await self.confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def leave_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ allows user to leave the plan with the specified name

        Args:
            message (Message): message with the plan name
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self.parse_input(message)

            if "plan_name" not in arguments:
                raise ValueError("You need to specify a name for the plan you want to leave.")

            self._database.remove_person(message.chat.id, arguments["plan_name"], message.from_user.id)

            await self.confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def add_lesson(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ adds a lesson to the plan with the specified name

        Args:
            message (Message): message with the lesson arguments
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self.parse_input(message)
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a plan for the lesson.")
            
            new_lesson = lesson.Lesson(arguments)
            
            self._database.add_lesson(message.chat.id, arguments["plan_name"], arguments.get("day", 0), new_lesson)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return

    async def remove_lesson(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ removes a lesson from the plan with the specified name

        Args:
            message (Message): message with the lesson arguments
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self.parse_input(message)
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a plan for the lesson.")
            
            self._database.remove_lesson(message.chat.id, arguments["plan_name"], arguments.get("day", 0), arguments.get("idx", 0))
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def edit_lesson(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ edits a lesson in the plan with the specified name

        Args:
            message (Message): message with the lesson arguments
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self.parse_input(message)
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a plan for the lesson.")

            lesson_to_edit = self._database.get_lesson(message.chat.id, arguments["plan_name"], arguments.get("day", 0), arguments.get("idx", 0))
            
            lesson_to_edit.read_args(arguments)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def move_lesson(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        """ moves a lesson in the plan with the specified name

        Args:
            message (Message): message with the lesson arguments
            bot (async_telebot.AsyncTeleBot): bot to send messages with

        Raises:
            ValueError: if no plan name is provided

        """
        try:
            arguments = self.parse_input(message)
            
            if "plan_name" not in arguments:
                raise ValueError("You need to specify a plan for the lesson.")
            
            self._database.remove_lesson(message.chat.id, arguments["plan_name"], arguments.get("from-day", 0), arguments.get("from-idx", 0))
            self._database.add_lesson(message.chat.id, arguments["plan_name"], arguments.get("to-day", 0), arguments.get("to-idx", 0))
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return

    def save(self) -> None:
        self._database.save()
    
    def load(self) -> None:
        self._database.load()
    
    