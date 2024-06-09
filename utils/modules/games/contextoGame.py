import requests
from .game import Game

class ContextoGame(Game):
    def __init__(self, game_number) -> None:
        super().__init__()
        self.game_num = game_number
        self._guesses = set()
        self._last_guess = None
        self._scores = []
        self._request_url = f"https://api.contexto.me/machado/en/game/{game_number}/"
        self._max_scores = 20
        self._game_text = "Contexto, use /join_contexto to join."

        validity_check = dict(requests.get(self._request_url + "hi").json())
        if validity_check.get('error', False):
            raise ValueError("Invalid game idx")
    
    def guess(self, word: str) -> bool:
        if not self.game_started:
            return

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

        self._current_player_idx = (self._current_player_idx + 1) % len(self._players)

        if distance == 0:
            self.game_started = False
            return True

        return False
    
    def get_top_list(self) -> list[tuple[str, int, str]]:
        return self._scores + [self._last_guess]