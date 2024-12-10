""" Button picker for telegram """

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class ButtonPicker(InlineKeyboardMarkup):
    """ Button picker class """
    def __init__(self, buttons: list[dict[str, InlineKeyboardButton]],
                 prefix: str, user_id: int | None = None) -> None:
        """ Initialize the button picker """
        inline_buttons = []
        if user_id is None:
            buttons.append({"Cancel": "cancel"})
        else:
            buttons.append({"Cancel": f"cancel:{user_id}"})
        for button_list in buttons:
            inline_buttons.append([InlineKeyboardButton(text, callback_data=prefix + ":" + data)
                                   for text, data in button_list.items()])
        super().__init__(inline_buttons)

    @property
    def is_empty(self) -> bool:
        """ Check if the button picker is empty """
        return len(self.inline_keyboard) == 0
