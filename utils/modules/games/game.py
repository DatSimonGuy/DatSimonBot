class Game:
    def __init__(self) -> None:
        self._players = []
        self._current_player_idx = 0
        self.game_running = False
        self._owner = None
    
    def add_player(self, player) -> None:
        self._players.append(player)
    
    def start_game(self) -> None:
        self.game_running = True

    def set_owner(self, owner: int) -> None:
        self._owner = owner
    
    def end_game(self) -> None:
        self.game_running = False
    
    def is_owner(self, user_id: int) -> bool:
        return user_id == self._owner