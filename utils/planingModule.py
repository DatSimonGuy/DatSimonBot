import utils.types as types
import telebot.async_telebot as async_telebot
from telebot.types import Message, ReactionTypeEmoji
import datetime

class PlaningModule:
    def __init__(self, bot: async_telebot.AsyncTeleBot) -> None:
        self.database = types.Database("plans")
        self.load()
        bot.register_message_handler(self.new_plan, commands=["new_plan"], pass_bot=True)
        bot.register_message_handler(self.remove_plan, commands=["remove_plan"], pass_bot=True)
        bot.register_message_handler(self.get_plan, commands=["get_plan"], pass_bot=True)
        bot.register_message_handler(self.join_plan, commands=["join_plan"], pass_bot=True)
        bot.register_message_handler(self.leave_plan, commands=["leave_plan"], pass_bot=True)
        bot.register_message_handler(self.add_lesson, commands=["add_lesson"], pass_bot=True)
        bot.register_message_handler(self.remove_lesson, commands=["remove_lesson"], pass_bot=True)
        bot.register_message_handler(self.edit_lesson, commands=["edit_lesson"], pass_bot=True)

    async def confirm(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        await bot.set_message_reaction(message.chat.id, message.message_id, [ReactionTypeEmoji("👍")])

    async def new_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        try:
            new_plan_name = ' '.join(message.text.split()[1:])
        except IndexError:
            await bot.send_message(message.chat.id, "You need to specify a name for the new plan.")
            return
        try:
            self.database.new_plan(message.chat.id, new_plan_name)
        except ValueError:
            await bot.send_message(message.chat.id, "Plan already exists.")
        await self.confirm(message, bot)
        self.save()
    
    async def remove_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        try:
            plan_name = ' '.join(message.text.split()[1:])
        except IndexError:
            await bot.send_message(message.chat.id, "You need to specify a name for the plan you want to remove.")
            return
        try:
            self.database.remove_plan(message.chat.id, plan_name)
        except ValueError:
            await bot.send_message(message.chat.id, f"Plan {plan_name} does not exist.")
        await self.confirm(message, bot)
        self.save()

    async def get_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        try:
            plan_name = ' '.join(message.text.split()[1:])
        except IndexError:
            await bot.send_message(message.chat.id, "You need to specify a name for the plan you want to get.")
            return
        try:
            plan_message = ""
            for day in range(7):
                plan_message += f"Day {day}:\n"
                for lesson in self.database.get_plan(message.chat.id, plan_name).get_lessons(day):
                    plan_message += str(lesson)
                plan_message += "\n"
        except KeyError:
            await bot.send_message(message.chat.id, f"Plan {plan_name} does not exist.")
            return
        await bot.send_message(message.chat.id, plan_message)
    
    async def join_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        try:
            plan_name = ' '.join(message.text.split()[1:])
        except IndexError:
            await bot.send_message(message.chat.id, "You need to specify a name for the plan you want to join.")
            return
        try:
            self.database.add_person(message.chat.id, plan_name, message.from_user.id, message.from_user)
        except KeyError:
            await bot.send_message(message.chat.id, f"Plan {plan_name} does not exist.")
            return
        await self.confirm(message, bot)
        self.save()
    
    async def leave_plan(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        try:
            plan_name = ' '.join(message.text.split()[1:])
        except IndexError:
            await bot.send_message(message.chat.id, "You need to specify a name for the plan you want to leave.")
            return
        try:
            self.database.remove_person(message.chat.id, plan_name, message.from_user.id)
        except KeyError:
            await bot.send_message(message.chat.id, f"Plan {plan_name} does not exist.")
            return
        await self.confirm(message, bot)
        self.save()
    
    async def add_lesson(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        try:
            day = 0
            plan_name = ""
            lesson = types.Lesson()
            data = message.text.split("—")[1:]

            for arg in data:
                if arg.startswith("day"):
                    try:
                        day = int(arg.split()[1])
                    except ValueError:
                        await bot.send_message(message.chat.id, "Day must be an integer.")
                        return
                elif arg.startswith("start"):
                    try:
                        start_time = datetime.datetime.strptime(arg.split()[1], "%H:%M")
                        lesson.start = start_time.time()
                    except ValueError:
                        await bot.send_message(message.chat.id, "Time must be in the format HH:MM.")
                        return
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify the start time for the lesson.")
                        return
                elif arg.startswith("end"):
                    try:
                        end_time = datetime.datetime.strptime(arg.split()[1], "%H:%M")
                        lesson.end = end_time.time()
                    except ValueError:
                        await bot.send_message(message.chat.id, "Time must be in the format HH:MM.")
                        return
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify the end time for the lesson.")
                        return
                elif arg.startswith("subject"):
                    try:
                        lesson.subject = ' '.join(arg.split()[1:])
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify a subject for the lesson.")
                        return
                elif arg.startswith("room"):
                    try:
                        lesson.room = ' '.join(arg.split()[1:])
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify a room for the lesson.")
                        return
                elif arg.startswith("type"):
                    try:
                        lesson.type = types.LessonType.str_to_type(arg.split()[1])
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify a type for the lesson.")
                        return
                    except ValueError:
                        await bot.send_message(message.chat.id, "Invalid type.")
                        return
                elif arg.startswith("plan"):
                    try:
                        plan_name = ' '.join(arg.split()[1:])
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify a plan for the lesson.")
                        return
            try:
                self.database.add_lesson(message.chat.id, plan_name, day, lesson)
                self.save()
                await self.confirm(message, bot)
            except KeyError:
                await bot.send_message(message.chat.id, f"Plan {plan_name} does not exist.")
                return
        except IndexError:
            await bot.send_message(message.chat.id, "You need to specify at least plan name for the lesson.")
            return

    async def remove_lesson(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        try:
            day = 0
            plan_name = ""
            idx = 0
            data = message.text.split("—")[1:]
            
            for arg in data:
                if arg.startswith("day"):
                    try:
                        day = int(arg.split()[1])
                    except ValueError:
                        await bot.send_message(message.chat.id, "Day must be an integer.")
                        return
                elif arg.startswith("idx"):
                    try:
                        idx = int(arg.split()[1])
                    except ValueError:
                        await bot.send_message(message.chat.id, "Index must be an integer.")
                        return
                elif arg.startswith("plan"):
                    try:
                        plan_name = ' '.join(arg.split()[1:])
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify a plan for the lesson.")
                        return
            try:
                self.database.remove_lesson(message.chat.id, plan_name, day, idx)
                self.save()
                await self.confirm(message, bot)
            except KeyError:
                await bot.send_message(message.chat.id, f"Plan {plan_name} does not exist.")
                return
        except IndexError:
            await bot.send_message(message.chat.id, "You need to specify a day, index and plan for the lesson.")
            return
    
    async def edit_lesson(self, message: Message, bot: async_telebot.AsyncTeleBot) -> None:
        try:
            day = 0
            plan_name = ""
            idx = 0
            data = message.text.split("—")[1:]

            subject = None
            start_time = None
            end_time = None
            room = None
            lesson_type = None

            for arg in data:
                if arg.startswith("day"):
                    try:
                        day = int(arg.split()[1])
                    except ValueError:
                        await bot.send_message(message.chat.id, "Day must be an integer.")
                        return
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify a day for the lesson.")
                        return
                elif arg.startswith("idx"):
                    try:
                        idx = int(arg.split()[1])
                    except ValueError:
                        await bot.send_message(message.chat.id, "Index must be an integer.")
                        return
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify an index for the lesson.")
                        return
                elif arg.startswith("plan"):
                    try:
                        plan_name = ' '.join(arg.split()[1:])
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify a plan for the lesson.")
                        return
                elif arg.startswith("start"):
                    try:
                        start_time = datetime.datetime.strptime(arg.split()[1], "%H:%M")
                    except ValueError:
                        await bot.send_message(message.chat.id, "Time must be in the format HH:MM.")
                        return
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify the start time for the lesson.")
                        return
                elif arg.startswith("end"):
                    try:
                        end_time = datetime.datetime.strptime(arg.split()[1], "%H:%M")
                    except ValueError:
                        await bot.send_message(message.chat.id, "Time must be in the format HH:MM.")
                        return
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify the end time for the lesson.")
                        return
                elif arg.startswith("subject"):
                    try:
                        subject = ' '.join(arg.split()[1:])
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify a subject for the lesson.")
                        return
                elif arg.startswith("room"):
                    try:
                        room = ' '.join(arg.split()[1:])
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify a room for the lesson.")
                        return
                elif arg.startswith("type"):
                    try:
                        lesson_type = types.LessonType.str_to_type(arg.split()[1])
                    except IndexError:
                        await bot.send_message(message.chat.id, "You need to specify a type for the lesson.")
                        return
                    except ValueError:
                        await bot.send_message(message.chat.id, "Invalid type.")
                        return
            try:
                lesson = self.database.get_plan(message.chat.id, plan_name).get_lessons(day)[idx]
                
                if subject:
                    lesson.subject = subject
                if start_time:
                    lesson.start = start_time.time()
                if end_time:
                    lesson.end = end_time.time()
                if room:
                    lesson.room = room
                if lesson_type:
                    lesson.type = lesson_type
                self.save()
                self.database.get_plan(message.chat.id, plan_name).get_lessons(day).sort()
                await self.confirm(message, bot)
            except KeyError:
                await bot.send_message(message.chat.id, f"Plan {plan_name} does not exist.")
                return
            except IndexError:
                await bot.send_message(message.chat.id, "Index out of range.")
                return
        except IndexError:
            await bot.send_message(message.chat.id, "You need to specify a day, index and plan for the lesson.")
            return
        
    def save(self) -> None:
        self.database.save()
    
    def load(self) -> None:
        self.database.load()
    
    