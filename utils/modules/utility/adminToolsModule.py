from telebot.async_telebot import AsyncTeleBot
from ..dsbModule import DsbModule
import jsonpickle
from dotenv import load_dotenv
import os
from telebot.types import Message
from telebot.asyncio_helper import ApiException

class AdminTools(DsbModule):
    def __init__(self, bot: AsyncTeleBot) -> None:
        commands = {
            "add_admin": self.add_admin,
            "remove_admin": self.remove_admin
        }
        super().__init__(bot, commands)
        try:
            with open("data/admins.json", "r") as f:
                self.admins = set(jsonpickle.decode(f.read()))
        except FileNotFoundError:
            load_dotenv()
            self.admins = set([int(os.getenv("DEV_ID"))])
            with open("data/admins.json", "w") as f:
                f.write(jsonpickle.encode(self.admins))
    
    async def add_admin(self, message: Message, bot: AsyncTeleBot) -> None:
        raise NotImplementedError("I neeed to figure out how to get the user id from the message without replying.")
        
        if not message.from_user.id in self.admins:
            return
        
        args = self._parse_input(message, "user")
        try:
            user = await bot.get_chat(args["user"])
            user_id = user.id
            self.admins.add(user_id)
            with open("data/admins.json", "w") as f:
                f.write(jsonpickle.encode(self.admins))
            await self._confirm(message, bot)
        except ApiException:
            await bot.send_message(message.chat.id, "User not found.")
            return
    
    async def remove_admin(self, message: Message, bot: AsyncTeleBot) -> None:
        raise NotImplementedError("I neeed to figure out how to get the user id from the message without replying.")

        if not message.from_user.id in self.admins:
            return
        
        args = self._parse_input(message, "user")
        try:
            user = await bot.get_chat(args["user"])
            user_id = user.id
            self.admins.remove(user_id)
            with open("data/admins.json", "w") as f:
                f.write(jsonpickle.encode(self.admins))
            await self._confirm(message, bot)
        except ApiException:
            await bot.send_message(message.chat.id, "User not found.")
            return
