from telebot.async_telebot import AsyncTeleBot
from ..dsbModule import DsbModule
import jsonpickle
from dotenv import load_dotenv
import os

class AdminTools(DsbModule):
    def __init__(self, bot: AsyncTeleBot) -> None:
        commands = {
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