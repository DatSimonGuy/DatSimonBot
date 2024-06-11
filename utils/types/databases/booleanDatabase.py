from .database import Database

class BooleanDatabase(Database):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._data = {}
    
    def setArg(self, group_id, key: str, value: bool) -> None:
        if group_id not in self._data:
            self._data[group_id] = {}
        self._data[group_id][key] = value
        self.save()
    
    def getArg(self, group_id, key: str) -> bool:
        return self._data.get(group_id, {}).get(key, False)