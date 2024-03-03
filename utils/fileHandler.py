import os
import jsonpickle

def SaveData(file_path, object, mode: int = 0):
    if mode == 1:
        file_path = f"data/groups/{file_path}"
    else:
        file_path = f"data/{file_path}"

    if mode != 2:
        file_path += '.json'

    try:
        with open(file_path, "w") as f:
            json_data = jsonpickle.encode(object, make_refs=False, keys=True, indent=1)
            f.write(json_data)
    except FileNotFoundError:
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir, exist_ok=True)
        SaveData(file_path, object, 2)

def ReadData(file_path: str, mode: int = 0):
    if mode == 1:
        file_path = f"data/groups/{file_path}"
    else:
        file_path = f"data/{file_path}"
    file_path += '.json'
    try:
        with open(file_path, "r") as f:
            return jsonpickle.decode(f.read(), keys=True)
    except FileNotFoundError:
        return None

def Delete(file_path : str, mode : int = 0):
    if mode == 1:
        file_path = f"data/groups/{file_path}"
    else:
        file_path = f"data/{file_path}"
    file_path += '.json'
    try:
        os.remove(file_path)
    except NotADirectoryError:
        return
