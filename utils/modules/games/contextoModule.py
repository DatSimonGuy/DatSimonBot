from .gameModule import GameModule
from .contextoGame import ContextoGame
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot
import jsonpickle
import os

class ContextoModule(GameModule):
    used = True

    def __init__(self, bot):
        super().__init__(bot)
        self._commands = {
            "contexto": self._start_game,
            "c_end": self._end_game,
            "c": self.guess,
            "join_contexto": self._join_game,
            "c_join": self._join_game,
            "c_leave": self._leave_game,
            "c_instant": self._instant_start,
        }
        os.makedirs("data/games/contexto", exist_ok=True)
        self._game_class = ContextoGame
        try:
            with open("data/games/contexto/save.json", "r") as f:
                self._played_games = jsonpickle.decode(f.read(), keys=True)
        except FileNotFoundError:
            self._played_games = {}
    
    async def _new_game(self, message: Message) -> None:
        self._games[message.chat.id] = self._game_class(max(self._played_games.get(message.chat.id, [0])) + 1)
    
    async def _start_game(self, message: Message, bot: AsyncTeleBot) -> None:
        await super()._start_game(message, bot)
    
    async def _end_game(self, message: Message, bot: AsyncTeleBot) -> None:
        await super()._end_game(message, bot)
        self._played_games[message.chat.id] = self._played_games.get(message.chat.id, []) + [self._games[message.chat.id].game_num]
        with open("data/games/contexto/save.json", "w") as f:
            f.write(jsonpickle.encode(self._played_games, keys=True))
    
    async def guess(self, message: Message, bot: AsyncTeleBot) -> None:
        """ Guess a word in the game

        Args:
            message (Message): message containing the guess
            bot (AsyncTeleBot): bot to send messages

        """
        if message.chat.id not in self._games:
            await bot.send_message(message.chat.id, "No game started!")
            return
        
        if not self._games[message.chat.id].game_running:
            await bot.send_message(message.chat.id, "Game has ended!")
            return
        
        if not self._games[message.chat.id].current_player().id == message.from_user.id:
            await bot.send_message(message.chat.id, "Not your turn")
            return
        
        guess = self._parse_input(message, "word")["word"]
        if self._games[message.chat.id].guess(guess):
            await bot.send_message(message.chat.id, "Game won! The word was {}".format(guess))
            await self._end_game(message, bot)
        else:
            await bot.send_message(message.chat.id, self._games[message.chat.id].get_top_list())
    