from telebot.async_telebot import AsyncTeleBot
from ..dsbModule import DsbModule
from ...types.databases.database import Database

class DatabaseModule(DsbModule):
    def __init__(self, bot: AsyncTeleBot, commands: dict) -> None:
        super().__init__(bot, commands)
        self._database: Database = None
    
    def _save(self) -> None:
        self._database.save()
    
    def _load(self) -> None:
        self._database.load()

