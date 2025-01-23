""" Button picker for telegram """

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class CallbackData:
    """ Data passed in button callback """
    def __init__(self, prefix: str, user_id: int, data: dict):
        self._function = prefix
        self._data = data
        self._user_id = user_id

    @property
    def prefix(self) -> str:
        """ Get function prefix """
        return self._function

    @property
    def data(self) -> dict:
        """ Get callback data """
        return self._data

    @property
    def caller(self) -> int:
        """ Get caller id """
        return self._user_id

    def add_value(self, key, value) -> dict:
        """ Add value and return data """
        self._data[key] = value
        return self._data

class ButtonPicker(InlineKeyboardMarkup):
    """ Button picker class """
    def __init__(self, buttons: list,
                 prefix: str, user_id: int) -> None:
        """ Initialize the button picker """
        inline_buttons = []
        buttons.append({"Cancel": ["cancel"]})
        for i, button in enumerate(buttons):
            inline_buttons.append(InlineKeyboardButton(button[0],
                                  callback_data=(i, CallbackData(prefix,
                                  user_id, button[1]))))
        super().__init__(inline_buttons)

    @property
    def is_empty(self) -> bool:
        """ Check if the button picker is empty """
        return len(self.inline_keyboard) == 0
