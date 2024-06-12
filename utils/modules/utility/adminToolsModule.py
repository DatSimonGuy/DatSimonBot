from telebot.async_telebot import AsyncTeleBot
from .databaseModule import DatabaseModule
from ...types.databases.keyDatabase import KeyDatabase
from telebot.types import Message
from dotenv import load_dotenv
import os

class AdminTools(DatabaseModule):
    def __init__(self, bot: AsyncTeleBot, database: KeyDatabase) -> None:
        commands = {
            "add_admin": self._add_admin
        }
        super().__init__(bot, commands)

        self._database: KeyDatabase = database

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