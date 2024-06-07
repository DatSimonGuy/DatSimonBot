from telebot.async_telebot import AsyncTeleBot
from .dsbModule import DsbModule
from telebot.types import Message
import time

class GameModule(DsbModule):
    def __init__(self, bot: AsyncTeleBot) -> None:
        super().__init__(bot)
        self._participants = []
        self.game_started = False
        self.game_start_time = 20 # seconds
    
    async def _join_game(self, message: Message, bot: AsyncTeleBot):
        if self.game_started == True:
            await bot.reply_to(message, "Game in progress")

        if message.from_user.id in self._participants:
            await bot.reply_to(message, "You are already in the game")
            return

        self._participants.append(message.from_user.id)
    
    async def _leave_game(self, message: Message, bot: AsyncTeleBot):
        if self.game_started == True:
            await bot.reply_to(message, "Game in progress")

        if message.from_user.id not in self._participants:
            await bot.reply_to(message, "You are not in the game")
            return
        
        self._participants.remove(message.from_user.id)
    
    async def _start_game(self, message: Message, bot: AsyncTeleBot):
        if self.game_started:
            await bot.reply_to(message, "The game has already been started")
            return

        minutes = self.game_start_time // 60
        seconds = self.game_start_time % 60
        sent_message = await bot.send_message(message.chat.id, "Starting soon: {:02d}:{:02d}".format(minutes, seconds))

        for i in range(self.game_start_time):
            minutes = (self.game_start_time - i) // 60
            seconds = (self.game_start_time - i) % 60
            await bot.edit_message_text("Starting soon: {:02d}:{:02d}".format(minutes, seconds), sent_message.id, sent_message.chat.id)
            time.sleep(1)
        
        self.game(bot)
    
    async def game(self, bot: AsyncTeleBot):
        pass
        
