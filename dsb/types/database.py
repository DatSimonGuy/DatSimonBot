""" Database for dsb """

import os
import jsonpickle

class Table:
    """ Table for database """
    def __init__(self, name: str, columns: list[tuple[str, type, bool]], path: str):
        self._name = name
        self._columns = columns
        self._columns.insert(0, ("id", int, not any(column[2] for column in columns)))
        self._save_path = path
        self._rows = {}
        self._len = 0

    @property
    def keys(self) -> list[str]:
        """ Get the keys of the table """
        return [column[0] for column in self._columns if column[2]]

    def add_row(self, row: list) -> None:
        """ Add a row to the table """
        row.insert(0, self._len)
        for i, element in enumerate(row):
            if not isinstance(element, self._columns[i][1]):
                raise ValueError(f"Element {element} is not of declared type {self._columns[i][1]}")
        key = tuple(row[i] for i, column in enumerate(self._columns) if column[2])
        self._rows[key] = row
        self._len += 1

    def remove_row(self, key: tuple | None = None,
                   check_function: callable = lambda x: True) -> None:
        """ Remove a row from the table """
        if key is None:
            row_iterator = (row for row in self._rows if check_function(row))
            row = next(row_iterator, None)
            if not row:
                return
            key = tuple(row[i] for i, column in enumerate(self._columns) if column[2])
        if key is None:
            return
        self._rows.pop(key)

    def get_row(self, key: tuple | None = None, check_function: callable = lambda x: True) -> list:
        """ Get a row from the table """
        if key is None:
            row_iterator = (row for row in self._rows.values() if check_function(row))
            return next(row_iterator, None)
        return self._rows.get(key, None)

    def get_rows(self, check_function: callable = lambda x: True) -> list[list]:
        """ Get all rows from the table, skips rows that don't pass the check function """
        return [row for row in self._rows.values() if check_function(row)]

    def remove_rows(self, check_function: callable = lambda x: False) -> None:
        """ Remove all rows from the table that don't pass the check function """
        self._rows = [row for row in self._rows if check_function(row)]

    def replace_row(self, key: tuple, row: list) -> None:
        """ Replace a row in the table """
        self._rows[key] = row

    def get_column(self, index: int) -> list[list]:
        """ Get a column from the table """
        return [row[index] for row in self._rows]

    def get_columns(self, columns: list[int]) -> list[list[list]]:
        """ Get all columns from the table """
        return [[row[i] for row in self._rows] for i in columns]

    def save(self) -> None:
        """ Save the table to the file """
        with open(os.path.join(self._save_path, f"{self._name}.json"),
                  "w", encoding="utf-8") as file:
            file.write(jsonpickle.encode(self, keys=True))

class Database:
    """ Database for dsb """
    def __init__(self, directory: str, name: str):
        self._directory = directory
        self._name = name
        os.makedirs(self._directory, exist_ok=True)

    @property
    def directory(self) -> str:
        """ Directory of the database """
        return self._directory

    @property
    def name(self) -> str:
        """ Name of the database """
        return self._name

    def add_table(self, name: str, columns: list[tuple[str, type, bool]],
                  exist_ok: bool = False) -> None:
        """ Add a table to the database """
        if os.path.exists(os.path.join(self._directory, f"{name}.json")):
            if exist_ok:
                return
            raise FileExistsError(f"Table {name} already exists")
        new_table = Table(name, columns, self._directory)
        new_table.save()

    def remove_table(self, name: str) -> None:
        """ Remove a table from the database """
        os.remove(os.path.join(self._directory, name))

    def get_table(self, name: str) -> Table:
        """ Get a table from the database """
        with open(os.path.join(self._directory, f"{name}.json"), "r", encoding="utf-8") as file:
            return jsonpickle.decode(file.read(), keys=True)

    def save_file(self, file: bytes, path: str) -> None:
        """ Save a file to the database """
        with open(os.path.join(self._directory, path), "wb") as file_:
            file_.write(file)

    def load_file(self, path: str) -> bytes:
        """ Load a file from the database """
        with open(os.path.join(self._directory, path), "rb") as file:
            return file.read()

    def remove_file(self, path: str) -> None:
        """ Remove a file from the database """
        os.remove(os.path.join(self._directory, path))

    def list_all(self, path: str) -> list[str]:
        """ List all files in a directory """
        return os.listdir(os.path.join(self._directory, path))
