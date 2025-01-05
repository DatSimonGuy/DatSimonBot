""" Button picker for telegram """

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class CallbackData:
    """ Data passed in button callback """
    def __init__(self, prefix: str, user_id: int, data: list[str]):
        self._function = prefix
        self._data = data
        self._user_id = user_id

    @property
    def prefix(self) -> str:
        """ Get function prefix """
        return self._function

    @property
    def data(self) -> list:
        """ Get callback data """
        return self._data

    @property
    def caller(self) -> int:
        """ Get caller id """
        return self._user_id

    def add_value(self, value) -> list:
        """ Add value to the data """
        self._data.append(str(value))
        return self._data

class ButtonPicker(InlineKeyboardMarkup):
    """ Button picker class """
    def __init__(self, buttons: list[dict[str, list]],
                 prefix: str, user_id: int) -> None:
        """ Initialize the button picker """
        inline_buttons = []
        buttons.append({"Cancel": ["cancel"]})
        for button_list in buttons:
            inline_buttons.append([InlineKeyboardButton(item[0],
                                   callback_data=(i, CallbackData(prefix, user_id, item[1])))
                                   for i, item in enumerate(button_list.items())])
        super().__init__(inline_buttons)

    @property
    def is_empty(self) -> bool:
        """ Check if the button picker is empty """
        return len(self.inline_keyboard) == 0
