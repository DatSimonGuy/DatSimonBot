from telebot.async_telebot import AsyncTeleBot
from .databaseModule import DatabaseModule
from ...types.databases.keyDatabase import KeyDatabase
from telebot.types import Message

class AdminTools(DatabaseModule):
    used = False
    
    def __init__(self, bot: AsyncTeleBot, people_database: KeyDatabase) -> None:
        super().__init__(bot)

        self._commands = {
            "add_admin": self._add_admin,
            "remove_admin": self._remove_admin,
            "see_admins": self._see_admins
        }

        self._database: KeyDatabase = people_database

    async def _add_admin(self, message: Message, bot: AsyncTeleBot):
        if not self._database.getArg(message.from_user.id, "admin"):
            await bot.reply_to(message, "You are not this bot's admin")
            return

        try:
            person = self._parse_input(message, "username")["username"]

            person = person[1:]

            criteria = {
                "name": person
            }

            matching = self._database.findMatching(criteria)

            if len(matching) == 0:
                await bot.reply_to(message, "I don't know them yet")
                return
            
            id = matching[0]

            self._database.setArg(id, "admin", True)
            await self._confirm(message, bot)
        except ValueError:
            await bot.reply_to(message, "No username specified")
    
    async def _remove_admin(self, message: Message, bot: AsyncTeleBot):
        if not self._database.getArg(message.from_user.id, "admin"):
            await bot.reply_to(message, "You are not this bot's admin")
            return

        try:
            person = self._parse_input(message, "username")

            person = person[1:]

            criteria = {
                "name": person
            }

            matching = self._database.findMatching(criteria)

            if len(matching) == 0:
                await bot.reply_to(message, "I don't know them yet")
                return
            
            id = matching[0]

            self._database.setArg(id, "admin", False)
            await self._confirm(message, bot)
        except ValueError:
            await bot.reply_to(message, "No username specified")
    
    def _see_admins(self):
        raise NotImplementedError("This function is not implemented yet")