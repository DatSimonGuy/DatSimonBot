""" Database module for the DSB project. """

import os
import shutil
from typing import Any
from rich.tree import Tree
import jsonpickle

class Database:
    """ Database module for the DSB project """
    name = "Database"
    def __init__(self, path = "dsb/database") -> None:
        self._directory = path
        os.makedirs(self._directory, exist_ok=True)

    def save(self, data: dict, subdir: str, filename: str, unpickable: bool = True) -> bool:
        """ Save data to the database. """
        os.makedirs(f"{self._directory}/{subdir}", exist_ok=True)
        try:
            with open(f"{self._directory}/{subdir}/{filename}.json", "w", encoding='utf-8') as file:
                file.write(jsonpickle.encode(data, keys=True, indent=4, unpicklable=unpickable))
        except OSError:
            return False
        return True

    def save_image(self, data: bytes, subdir: str, filename: str) -> bool:
        """ Save image to the database. """
        os.makedirs(f"{self._directory}/{subdir}", exist_ok=True)
        try:
            with open(f"{self._directory}/{subdir}/{filename}.png", "wb") as file:
                file.write(data)
        except OSError:
            return False
        return True

    def load(self, subdir: str, filename: str, default: Any = None) -> dict:
        """ Load data from the database. """
        try:
            with open(f"{self._directory}/{subdir}/{filename}.json", "r", encoding='utf-8') as file:
                data = jsonpickle.decode(file.read(), keys=True)
            return data
        except FileNotFoundError:
            if default is None:
                return {}
            return default

    def list_all(self, subdir: str) -> list[str]:
        """ List all files in the directory. """
        try:
            return os.listdir(f"{self._directory}/{subdir}")
        except FileNotFoundError:
            return []

    def load_image(self, subdir: str, filename: str) -> bytes:
        """ Load image from the database. """
        try:
            with open(f"{self._directory}/{subdir}/{filename}.png", "rb") as file:
                data = file.read()
            return data
        except FileNotFoundError:
            return b""

    def create_dir(self, subdir: str) -> bool:
        """ Create a directory in the database. """
        try:
            os.makedirs(f"{self._directory}/{subdir}", exist_ok=True)
            return True
        except OSError:
            return False

    def delete_dir(self, subdir: str) -> bool:
        """ Delete a directory from the database. """
        try:
            shutil.rmtree(f"{self._directory}/{subdir}")
            return True
        except FileNotFoundError:
            return False

    def delete(self, subdir: str, filename: str) -> bool:
        """ Delete data from the database. """
        try:
            os.unlink(f"{self._directory}/{subdir}/{filename}.json")
            if not os.listdir(f"{self._directory}/{subdir}"):
                os.rmdir(f"{self._directory}/{subdir}")
            return True
        except FileNotFoundError:
            return False

    def delete_image(self, subdir: str, filename: str) -> bool:
        """ Delete image from the database. """
        try:
            os.unlink(f"{self._directory}/{subdir}/{filename}.png")
            if not os.listdir(f"{self._directory}/{subdir}"):
                os.rmdir(f"{self._directory}/{subdir}")
            return True
        except FileNotFoundError:
            return False

    def tree(self) -> Tree:
        """ Return the directory tree. """
        tree = Tree(f"{self._directory}")
        branches = {f"{self._directory}": tree}
        for root, _, files in os.walk(self._directory):
            if root not in branches:
                branches[root] = branches[os.path.dirname(root)].add(os.path.basename(root))
            for file in files:
                branches[root].add(file)
        return tree

    def backup(self) -> bytes:
        """ Create a backup of the database. """
        try:
            shutil.make_archive(self._directory, 'zip', self._directory)
            with open(f"{self._directory}.zip", "rb") as file:
                data = file.read()
        except OSError:
            return b""
        finally:
            os.remove(f"{self._directory}.zip")
        return data
