""" Database class """

import os
import jsonpickle

class Database:
    """ Class for handling the persistance data """
    def __init__(self, path: str) -> None:
        """ Initialize the database """
        self._path = path
        self.__setup()

    def __setup(self) -> None:
        """ Create the directories for the database """
        os.makedirs(f"{self._path}/user_data", exist_ok=True)
        os.makedirs(f"{self._path}/chat_data", exist_ok=True)
        os.makedirs(f"{self._path}/bot_data", exist_ok=True)
        os.makedirs(f"{self._path}/files", exist_ok=True)

    def get_chat_data(self, chat_id: int) -> dict:
        """ Get the chat data """
        try:
            with open(f"{self._path}/chat_data/{chat_id}.json", "r", encoding='utf-8') as f:
                data = jsonpickle.decode(f.read(), keys=True)
                if data is None:
                    return {}
                return data
        except FileNotFoundError:
            return {}

    def get_user_data(self, user_id: int) -> dict:
        """ Get the user data """
        try:
            with open(f"{self._path}/user_data/{user_id}.json", "r", encoding='utf-8') as f:
                data = jsonpickle.decode(f.read(), keys=True)
                if data is None:
                    return {}
                return data
        except FileNotFoundError:
            return {}

    def get_bot_data(self) -> dict:
        """ Get the bot data """
        try:
            with open(f"{self._path}/bot_data.json", "r", encoding='utf-8') as f:
                data = jsonpickle.decode(f.read(), keys=True)
                if data is None:
                    return {}
                return data
        except FileNotFoundError:
            return {}

    def get_json(self, file_name: str) -> dict:
        """ Get the file data """
        try:
            with open(f"{self._path}/files/{file_name}.json", "r", encoding='utf-8') as f:
                data = jsonpickle.decode(f.read(), keys=True)
                if data is None:
                    return {}
                return data
        except FileNotFoundError:
            return {}

    def save_json(self, file_name: str, data: dict) -> None:
        """ Save the file data """
        with open(f"{self._path}/files/{file_name}.json", "w", encoding='utf-8') as f:
            f.write(jsonpickle.encode(data, keys=True, indent=4))

    def get_image(self, group_id: int, file_name: str) -> bytes:
        """ Get the image data """
        try:
            with open(f"{self._path}/{group_id}/images/{file_name}.jpg", "rb") as f:
                data = f.read()
                if data is None:
                    return b""
                return data
        except FileNotFoundError:
            return b""

    def save_image(self, group_id: int, file_name: str, data: bytes) -> None:
        """ Save the image data """
        os.makedirs(f"{self._path}/{group_id}/images", exist_ok=True)
        with open(f"{self._path}/{group_id}/images/{file_name}.jpg", "wb") as f:
            f.write(data)

    def delete_json(self, file_name: str) -> None:
        """ Delete the file data """
        try:
            os.remove(f"{self._path}/files/{file_name}.json")
        except FileNotFoundError:
            pass
        except PermissionError:
            pass

    def delete_image(self, group_id: int, file_name: str) -> None:
        """ Delete the image data """
        try:
            os.remove(f"{self._path}/{group_id}/images/{file_name}.jpg")
        except FileNotFoundError:
            pass
        except PermissionError:
            pass

    def list_files(self, subdir: str) -> list[str]:
        """ List all files in a directory """
        try:
            return os.listdir(os.path.join(self._path, subdir))
        except FileNotFoundError:
            return []
