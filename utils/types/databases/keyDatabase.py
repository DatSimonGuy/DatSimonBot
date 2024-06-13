from .database import Database

class KeyDatabase(Database):
    def __init__(self, path: str, num: int = 0) -> None:
        super().__init__(path)
        self._num = num
        self._data: dict[any, dict[str]] = {}
    
    def setArg(self, id: any, key: str, value) -> None:
        if id not in self._data:
            self._data[id] = {}
        self._data[id][key] = value
        self.save(self._num)
    
    def load(self) -> None:
        return super().load(self._num)
    
    def getArg(self, id, key: str):
        """ gets specified key from an id

        Args:
            id (Any): id from which the key will be taken
            key (str): the wanted key
        
        Returns:
            Any: value that was found
            None: if no value was found

        """
        return self._data.get(id, {}).get(key, None)

    def findMatching(self, args: dict[str]) -> list:
        """ returns all matching database entries
        
        Args:
            args (dict[str, any]): Dict of keys and their values to match
        
        Returns:
            list: List of found entries ids

        """
        found = []
        valid = False
        for id in self._data:
            for key, val in self._data[id].items():
                if key in args and val != args[key]:
                    valid = False
                    break
                else:
                    valid = True
            if valid:
                found.append(id)
                valid = False
        return found
    
    def find(self, function) -> list:
        """ returns all matching database entries
        
        Args:
            function (function): a function that will determine if the key is valid, takes key and value as params
        
        Returns:
            list: List of found entries ids

        """
        found = []
        valid = False
        for id in self._data:
            for key, val in self._data[id].items():
                if not function(key, val):
                    valid = False
                    break
                else:
                    valid = True
            if valid:
                found.append(id)
                valid = False
        return found
    
    def exists(self, id) -> bool:
        return id in self._data
    
    def get_all_entries(self) -> list[int]:
        return list(self._data.keys())
        