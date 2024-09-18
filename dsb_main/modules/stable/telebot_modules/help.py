""" Telebot help module """

from telegram import Update
from .base.base_module import BaseModule

class Help(BaseModule):
    """ Help module """
    def __init__(self, ptb, telebot_module) -> None:
        super().__init__(ptb, telebot_module)
        self._handlers = {
            "help": self._help
        }
        self._descriptions = {
            "help": "Display help message"
        }

    async def _help(self, update: Update, _) -> None:
        """ Display help message """
        help_message = "Available commands:\n"
        for command, desc in self._telebot_module.commands.items():
            help_message += f"{command} - {desc}\n"
        await update.message.reply_text(help_message)
