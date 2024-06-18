from telebot.async_telebot import AsyncTeleBot
from ..dsbModule import DsbModule
from ...types.databases.database import Database

class DatabaseModule(DsbModule):
    used = False
    
    def __init__(self, bot: AsyncTeleBot, *args, **kwargs) -> None:
        super().__init__(bot)
        self._database: Database = None
    
    def _save(self) -> None:
        self._database.save()
    
    def _load(self) -> None:
        self._database.load()

