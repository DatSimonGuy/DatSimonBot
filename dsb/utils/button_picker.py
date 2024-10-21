""" Button picker for telegram """

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class ButtonPicker(InlineKeyboardMarkup):
    """ Button picker class """
    def __init__(self, buttons: list[dict[str, InlineKeyboardButton]], prefix: str) -> None:
        """ Initialize the button picker """
        inline_buttons = []
        for button in buttons:
            inline_buttons.append([InlineKeyboardButton(text, callback_data=prefix + ":" + data)
                                   for text, data in button.items()])
        super().__init__(inline_buttons)

    @property
    def is_empty(self) -> bool:
        """ Check if the button picker is empty """
        return len(self.inline_keyboard) == 0
