import os
from telegram.ext import BasePersistence
import jsonpickle

class CustomPersistance(BasePersistence):
    """ Custom persistence for the bot """
    def __init__(self, store_data = None, update_interval = 60,
                 store_path = "dsb/database/"):
        super().__init__(store_data, update_interval)
        self._store_path = store_path

    async def get_data(self, dir_name: str) -> dict:
        """ Get data from the directory """
        data = {}
        if not os.path.exists(os.path.join(self._store_path, dir_name)):
            return data
        for file_name in os.listdir(os.path.join(self._store_path, dir_name)):
            temp = await self.get_file_data(f"{dir_name}/{file_name.replace('.json', '')}")
            data.update({int(file_name.replace('.json', '')): temp})
        return data

    async def get_file_data(self, file_name: str) -> dict:
        """ Helper function """
        file_path = os.path.join(self._store_path, f"{file_name}.json")
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r", encoding='utf-8') as f:
            data = jsonpickle.decode(f.read(), keys=True)
            if data is None:
                return {}
            return data

    async def update_file_data(self, file_name: str, data) -> None:
        """ Helper function """
        file_path = os.path.join(self._store_path, f"{file_name}.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(jsonpickle.encode(data, keys=True, indent=4))

    async def drop_data(self, file_name: str) -> None:
        """ Helper function """
        file_path = os.path.join(self._store_path, f"{file_name}.json")
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(jsonpickle.encode({}, keys=True, indent=4))

    async def get_bot_data(self):
        return await self.get_file_data("bot_data")

    async def get_user_data(self):
        return await self.get_data("user_data")

    async def get_chat_data(self):
        return await self.get_data("chat_data")

    async def get_callback_data(self):
        return await self.get_file_data("callback_data")

    async def get_conversations(self, name: str):
        return await self.get_file_data(f"conversations/{name}")

    async def update_bot_data(self, data):
        return await self.update_file_data("bot_data", data)

    async def update_callback_data(self, data):
        return await self.update_file_data("callback_data", data)

    async def update_chat_data(self, chat_id: int, data):
        return await self.update_file_data(f"chat_data/{chat_id}", data)

    async def update_user_data(self, user_id: int, data):
        return await self.update_file_data(f"user_data/{user_id}", data)

    async def update_conversation(self, name: str, key, new_state: object | None):
        return await self.update_file_data(f"conversations/{name}", {key: new_state})

    async def refresh_bot_data(self, bot_data):
        pass

    async def refresh_user_data(self, user_id: int, user_data):
        pass

    async def refresh_chat_data(self, chat_id: int, chat_data):
        pass

    async def drop_user_data(self, user_id: int):
        return await self.drop_data(f"user_data/{user_id}")

    async def drop_chat_data(self, chat_id: int):
        return await self.drop_data(f"chat_data/{chat_id}")

    async def flush(self):
        pass
