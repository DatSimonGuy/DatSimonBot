from .database import Database

class TagDatabase(Database):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._data: dict[int, dict[str, list]]  = {}
    
    def add_tag(self, group_id: int, tag: str):
        try:
            self._data[group_id][tag] = []
        except KeyError:
            self._data[group_id] = {tag: []}
        self.save()
    
    def remove_tag(self, group_id: int, tag: str):
        if group_id not in self._data:
            self._data[group_id] = {}
        try:
            del self._data[group_id][tag]
            self.save()
        except KeyError:
            raise ValueError(f"Tag {tag} does not exist.")
    
    def add_element(self, group_id: int, tag: str, element):
        if group_id not in self._data:
            self._data[group_id] = {}
        
        if tag not in self._data[group_id]:
            raise ValueError(f"Tag {tag} does not exist.")

        self._data[group_id][tag].append(element)
        self.save()
    
    def remove_element(self, group_id: int, tag: str, element):
        if group_id not in self._data:
            self._data[group_id] = {}
        
        if tag not in self._data[group_id]:
            raise ValueError(f"Tag {tag} does not exist.")
        
        try:
            self._data[group_id][tag].remove(element)
            self.save()
        except ValueError:
            raise ValueError(f"Element {element} does not exist in tag {tag}.")
    
    def get_elements(self, group_id: int, tag: str):
        if group_id not in self._data:
            self._data[group_id] = {}
        
        if tag not in self._data[group_id]:
            raise ValueError(f"Tag {tag} does not exist.")
        
        return self._data[group_id][tag]
    
    def get_tags(self, group_id: int):
        return list(self._data[group_id].keys())