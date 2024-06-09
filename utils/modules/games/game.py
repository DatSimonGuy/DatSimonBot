from telebot.types import User
from telebot.async_telebot import AsyncTeleBot
import time

class Game:
    def __init__(self) -> None:
        self._players = []
        self._countdown = 20
        self._current_player_idx = 0
        self._start_time = 20 # seconds
        self.game_started = False
        self._game_text = "Game"

    def add_person(self, person: User) -> bool:
        person_id = person.id
        person_name = person.username
        if (person_id, person_name) in self._players:
            return False
        self.reset_countdown()
        self._players.append((person_id, person_name))
        return True
    
    def remove_person(self, person: User) -> bool:
        person_id = person.id
        person_name = person.username
        if not (person_id, person_name) in self._players:
            return False
        self._players.remove((person_id, person_name))
        return True
    
    async def start(self, group_id: int, bot: AsyncTeleBot):
        message = await bot.send_message(group_id, f"{self._game_text} starting soon: {self._countdown//60:02d}:{self._countdown%60:02d}")
        message_id = message.id
        while self._countdown:
            self._countdown -= 1
            time.sleep(1)
            if self._countdown % 5 == 0 or self._countdown <= 5:
                new_text = f"{self._game_text} starting soon: {self._countdown//60:02d}:{self._countdown%60:02d}"
                await bot.edit_message_text(new_text, group_id, message_id)
        self.game_started = True

    def reset_countdown(self):
        self._countdown = self._start_time + 2

    def current_player(self) -> tuple[int, str]:
        return self._players[self._current_player_idx]