from telebot.async_telebot import AsyncTeleBot
from ..dsbModule import DsbModule
from telebot.types import Message
from .game import Game
import asyncio
import threading

class GameModule(DsbModule):
    def __init__(self, bot: AsyncTeleBot, commands: dict) -> None:
        super().__init__(bot, commands)
        self._games: dict[int, Game] = {}
    
    async def _join_game(self, message: Message, bot: AsyncTeleBot) -> None:
        success = self._games[message.chat.id].add_person(message.from_user)
        if success:
            await self._confirm(message, bot)
    
    async def _leave_game(self, message: Message, bot: AsyncTeleBot) -> None:
        success = self._games[message.chat.id].remove_person(message.from_user)
        if success:
            await self._confirm(message, bot)
    
    async def _start_game(self, message: Message, bot: AsyncTeleBot):
        thread = threading.Thread(target=await self._games[message.chat.id].start(message.chat.id, bot))
        thread.start()
        
