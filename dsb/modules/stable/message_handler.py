""" Module for handling text messages """

from telegram import Update
from telegram.ext import filters
import telegram.ext
from dsb.types.module import BaseModule, prevent_edited

class MessageHandler(BaseModule):
    """ Module for handling text messages """
    def __init__(self, ptb, telebot) -> None:
        super().__init__(ptb, telebot)
        self._messages = {}
        self._message_handler = telegram.ext.MessageHandler(filters.ALL & ~filters.COMMAND,
                              self._handle_text)

    def add_handlers(self) -> None:
        """ Add handlers """
        self._bot.add_handler(self._message_handler)

    def remove_handlers(self) -> None:
        """ Remove handlers """
        self._bot.remove_handler(self._message_handler)

    @property
    def messages(self) -> dict:
        """ Returns the list of messages """
        return self._messages

    @prevent_edited
    async def _handle_text(self, update: Update, _) -> None:
        """ Handle text messages """
        if update.message.chat_id not in self._messages:
            self._messages[update.message.chat_id] = [update.message]
        else:
            self._messages[update.message.chat_id].append(update.message)
        for messages in self._messages.values():
            if len(messages) > 10:
                messages.pop(0)
