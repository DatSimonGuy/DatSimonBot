from ..dsbModule import DsbModule
from .game import Game
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot
import asyncio
from telebot.asyncio_helper import ApiTelegramException

class GameModule(DsbModule):
    def __init__(self, bot, commands: dict):
        super().__init__(bot, commands)
        self._games: dict[int, Game] = {}
        self._game_class = Game
    
    async def _new_game(self, message: Message) -> None:
        self._games[message.chat.id] = self._game_class()
    
    async def _start_game(self, message: Message, bot: AsyncTeleBot) -> None:
        await self._new_game(message)

        self._games[message.chat.id].add_player(message.from_user)

        self._games[message.chat.id].set_owner(message.from_user.id)

        countdown = 60
        
        sent_message = (await bot.send_message(message.chat.id, f"Game starting in {countdown} seconds"))

        while countdown > 0:
            if self._games[message.chat.id].game_running:
                return
            try:
                if countdown % 5 == 0 or countdown < 5:
                    await bot.edit_message_text(f"Game starting in {countdown} seconds", message.chat.id, sent_message.id)
            except ApiTelegramException:
                pass
            countdown -= 1
            await asyncio.sleep(1)
        
        if self._games[message.chat.id].game_running:
            return
        
        self._games[message.chat.id].start_game()

        await bot.send_message(message.chat.id, "Game started!")
        await bot.send_message(message.chat.id, f"Next player: {self._games[message.chat.id].current_player().username}")
    
    async def _end_game(self, message: Message, bot: AsyncTeleBot) -> None:
        if message.chat.id not in self._games:
            await bot.send_message(message.chat.id, "No game started!")
            return
        
        if self._games[message.chat.id].is_owner(message.from_user.id):
            self._games[message.chat.id].end_game()
            await bot.send_message(message.chat.id, "Game ended!")
        else:
            await bot.send_message(message.chat.id, "Only the owner can end the game!")
    
    async def _instant_start(self, message: Message, bot: AsyncTeleBot) -> None:
        if message.chat.id not in self._games:
            await bot.send_message(message.chat.id, "No game started!")
            return
        
        if not self._games[message.chat.id].is_owner(message.from_user.id):
            await bot.send_message(message.chat.id, "Only the owner can start the game!")
            return
        
        self._games[message.chat.id].start_game()
        await bot.send_message(message.chat.id, "Game started!")
        await bot.send_message(message.chat.id, f"Next player: {self._games[message.chat.id].current_player().username}")
    
    async def _join_game(self, message: Message, bot: AsyncTeleBot) -> None:
        if message.chat.id not in self._games:
            await bot.send_message(message.chat.id, "No game started!")
            return
        
        if message.from_user in self._games[message.chat.id]._players:
            await bot.send_message(message.chat.id, "Player already joined!")
            return
        
        self._games[message.chat.id].add_player(message.from_user)
        await bot.send_message(message.chat.id, "Player joined!")
    
    async def _leave_game(self, message: Message, bot: AsyncTeleBot):
        if message.chat.id not in self._games:
            await bot.send_message(message.chat.id, "No game started!")
            return
        
        if message.from_user not in self._games[message.chat.id]._players:
            await bot.send_message(message.chat.id, "Player not in game!")
            return
        
        self._games[message.chat.id]._players.remove(message.from_user)
        await bot.send_message(message.chat.id, "Player left!")
        

        