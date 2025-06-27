import os
import json
from pathlib import Path
from collections import defaultdict
from telegram.ext import BasePersistence
from typing import Any, Dict

class Persistence(BasePersistence):
    def __init__(self, path: str, store_data=None, update_interval = 60):
        super().__init__(store_data, update_interval)
        self._root_path = path

    async def get_data(self, path: str) -> Dict[str, Any]:
        path = f"{self._root_path}/{path}"
        
        if not os.path.exists(path):
            return {}
        
        if os.path.isdir(path):
            data = defaultdict(list)
            for file in os.listdir(path):
                data[int(Path(path).stem)] = self.get_data(f"{path}/{file}")
        else:
            with open(path, "r") as f:
                try:
                    data = json.loads(f.read())
                except json.JSONDecodeError:
                    return defaultdict(list)
            if data is None:
                return defaultdict(list)
        return data

    async def update_data(self, path, data):
        path = f"{self._root_path}/{path}"
        
        if not os.path.exists(path):
            raise FileNotFoundError("The specified path does not exist")

        with open(path, 'w') as f:
            f.write(json.dumps(data))

    async def drop_data(self, path: str):
        path = f"{self._root_path}/{path}"
        with open(path, 'w') as f:
            f.write(json.dumps({}))

    async def get_bot_data(self):
        return await self.get_data("bot_data.json")

    async def get_callback_data(self):
        return await self.get_data("callback_data.json")

    async def get_chat_data(self):
        return await self.get_data("chat_data/")

    async def get_user_data(self):
        return await self.get_data("user_data/")

    async def get_conversations(self, name):
        return await super().get_conversations(name)

    async def update_bot_data(self, data):
        return await self.update_data("bot_data.json", data)

    async def update_callback_data(self, data):
        return await self.update_data("callback_data.json", data)

    async def update_chat_data(self, chat_id, data):
        return await self.update_data(f"chat_data/{chat_id}.json", data)

    async def update_user_data(self, user_id, data):
        return await self.update_data(f"user_data/{user_id}.json", data)

    async def update_conversation(self, name, key, new_state):
        return await super().update_conversation(name, key, new_state)

    async def drop_chat_data(self, chat_id):
        return await self.drop_data(f"chat_data/{chat_id}.json")

    async def drop_user_data(self, user_id):
        return await self.drop_data(f"user_data/{user_id}.json")

class Database:
    def __init__(self, path: str):
        self._path = path
        self.__setup()
        self.persistance = Persistence(path)

    def __setup(self) -> None:
        """ Create the directories for the database """        
        for dir in ["user_data", "chat_data", "files"]:
            os.makedirs(f"{self._path}/{dir}", exist_ok=True)




    