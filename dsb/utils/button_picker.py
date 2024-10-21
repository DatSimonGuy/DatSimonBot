""" Button picker for telegram """

from typing import Callable, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CallbackContext
from telegram import Update

class ButtonPicker:
    """ Button picker class """
    def __init__(self, buttons: list[list[str]],
                 callback: Callable[[Update, CallbackContext, Any], None], *args) -> None:
        self._buttons = buttons
        self._callback = callback
        self._args = args

    def get_markup(self) -> InlineKeyboardMarkup:
        """ Get the markup """
        keyboard = []
        for row in self._buttons:
            keyboard.append([InlineKeyboardButton(text=button, callback_data=button)
                             for button in row])
        return InlineKeyboardMarkup(keyboard)

    def get_handler(self) -> CallbackQueryHandler:
        """ Get the handler """
        async def handler(update: Update, context: CallbackContext) -> None:
            query = update.callback_query
            await query.answer()
            self._callback(update, context, query.data, *self._args)
        return CallbackQueryHandler(handler)
