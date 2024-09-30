""" Telebot help module """

from telegram import Update
from telegram.ext import ContextTypes
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

    async def _help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Display help message """
        args, kwargs = self._get_args(context)
        if "botfather" in kwargs or "botfather" in args:
            help_message = "BotFather format commands:\n```\n"
            for command, desc in self._telebot_module.commands.items():
                help_message += f"{command} - {desc}\n"
            help_message += "```"
            await update.message.reply_text(help_message, parse_mode="Markdown")
        else:
            help_message = "Available commands:\n"
            for command, desc in self._telebot_module.commands.items():
                help_message += f"/{command} - {desc}\n"
            await update.message.reply_text(help_message)
