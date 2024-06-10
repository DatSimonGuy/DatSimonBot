import requests
from .game import Game

class ContextoGame(Game):
    def __init__(self, game_num: int) -> None:
        super().__init__()
        self.game_num = game_num
        self._guesses = set()
        self._last_guess = None
        self._scores = []
        self._request_url = f"https://api.contexto.me/machado/en/game/{self.game_num}/"
        self._max_scores = 20
        validity_check = dict(requests.get(self._request_url + "hi").json())
        if validity_check.get('error', False):
            raise ValueError("Invalid game idx")
    
    def guess(self, word: str) -> bool:
        """ Guess a word in the game and update the scores

        Args:
            word (str): word to guess

        Returns:
            bool: True if the word is correct, False otherwise

        """
        if not self.game_running:
            return

        self._current_player_idx = (self._current_player_idx + 1) % len(self._players)

        if word in self._guesses:
            self._last_guess = ("Already guessed", None, None)
            return False

        self._guesses.add(word)

        response = requests.get(self._request_url + word)

        try:
            distance = int(response.json()['distance'])
        except KeyError:
            self._last_guess = ("Invalid word", None, None)
            return False

        if distance <= 200:
            color = "🟢"
        elif distance < 1500:
            color = "🟡"
        else:
            color = "🔴"
        
        self._last_guess = (word, distance + 1, color)
        self._scores.append(self._last_guess)
        self._scores.sort(key=lambda x: x[1])

        if len(self._scores) > self._max_scores:
            self._scores.pop(self._max_scores)
        if distance == 0:
            self.game_running = False
            return True

        return False
    
    def get_top_list(self) -> str:
        list = "\n".join([f"{score[0]}: {score[1]} {score[2]}" for score in self._scores])
        list += f"\n\nLast guess: {self._last_guess[0]}: {self._last_guess[1]} {self._last_guess[2]}"
        list += f"\n\nCurrent player: {self._players[self._current_player_idx].username}"
        
        return list