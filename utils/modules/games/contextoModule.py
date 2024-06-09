from telebot.async_telebot import AsyncTeleBot
from .gameModule import GameModule
from telebot.types import Message
import jsonpickle
from .contextoGame import ContextoGame
import os

class ContextoModule(GameModule):
    def __init__(self, bot: AsyncTeleBot) -> None:
        self._commands = {
            "contexto": self._start_game,
            "c": self._guess,
            "join_contexto": self._join_game,
            "leave_contexto": self._leave_game
        }
        super().__init__(bot, self._commands)

        os.makedirs("data/games/contexto", exist_ok=True)

        try:
            with open("data/games/contexto/save.json", 'r') as f:
                self._completed_games = jsonpickle.decode(f.read(), keys=True)
        except FileNotFoundError:
            self._completed_games: dict[int, list] = {}

        self._games: dict[int, ContextoGame] = {}

    async def _start_game(self, message: Message, bot: AsyncTeleBot):
        current_game = self._games.get(message.chat.id, None)
        
        if current_game and current_game.game_started:
            return

        group_id = message.chat.id

        game_num = max(self._completed_games.get(group_id, [0])) + 1

        if game_num == 1:
            self._completed_games[group_id] = [1]
        else:
            self._completed_games[group_id].append(game_num)

        try:
            self._games[group_id] = ContextoGame(game_num)
            self._games[group_id].add_person(message.from_user)
            await super()._start_game(message, bot)
            next_player = self._games[group_id].current_player()
            await bot.send_message(group_id, f"Next player: {next_player[1]}")
        except ValueError:
            await bot.send_message(group_id, f"Unfortunatelly you have completed all of the games, try again later")
            return
    
    async def _guess(self, message: Message, bot: AsyncTeleBot):
        if message.from_user.id != self._games[message.chat.id].current_player()[0]:
            await bot.reply_to(message, "Not your turn")
            return
        try:
            arguments = self._parse_input(message, "word")

            if "word" not in arguments:
                await bot.reply_to(message, "Please write the word you want to guess")
            
            response = "Guessed words:\n"
            
            won = self._games[message.chat.id].guess(arguments["word"])

            top_guesses = self._games[message.chat.id].get_top_list()

            for i in range(len(top_guesses) - 1):
                response += f"{top_guesses[i][0]}: {top_guesses[i][1]} {top_guesses[i][2]}\n"

            response += f"Last guess: {top_guesses[-1][0]}: {top_guesses[-1][1]}"

            if won:
                await bot.reply_to(message, f"You won, congratulations! The word was: {arguments['word']}")

                completed_games = self._completed_games.get(message.chat.id, [])

                with open("data/games/contexto/save.json", 'w') as f:
                    f.write(jsonpickle.encode(completed_games, indent=1, keys=True))
                return

            await bot.send_message(message.chat.id, response)
            await bot.send_message(message.chat.id, f"Next player: {self._games[message.chat.id].current_player()[1]}")
        except ValueError as e:
            await bot.reply_to(message, str(e))
            return