import jsonpickle
import os

class Database:
    def __init__(self, path: str) -> None:
        self._path = path
        self._data = {}
        os.makedirs(self._path, exist_ok=True)
        
    def save(self, num: int = 0) -> None:
        """ saves the database to a file located at self.path/database.json
        """
        with open(self._path + f"/database{num if num else ''}.json", "w") as f:
            f.write(jsonpickle.encode(self._data, indent=1, keys=True))
    
    def load(self, num: int = 0) -> None:
        """ loads the database from a file located at self.path/database.json if it exists
        """
        try:
            with open(self._path + f"/database{num if num else ''}.json", "r") as f:
                self._data = jsonpickle.decode(f.read(), keys=True)
        except FileNotFoundError:
            return