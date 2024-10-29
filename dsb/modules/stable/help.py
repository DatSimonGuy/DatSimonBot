""" Telebot help module """

from telegram import Update
from telegram.ext import ContextTypes, Application
from dsb.types.module import BaseModule
from dsb.dsb import DSB

class Help(BaseModule):
    """ Help module """
    def __init__(self, ptb: Application, dsb: DSB) -> None:
        super().__init__(ptb, dsb)
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
            for command, desc in self._dsb.commands.items():
                help_message += f"{command} - {desc}\n"
            help_message += "```"
            await update.message.reply_text(help_message, parse_mode="Markdown")
        elif args:
            command = args[0]
            handler = self._dsb.get_handler(command)
            if not handler:
                await update.message.reply_text(f"Unknown command {command}")
                return
            await update.message.reply_text(str(handler.__doc__).replace("    ", ""))
        else:
            help_message = "Available commands:\n"
            for command, desc in self._dsb.commands.items():
                help_message += f"/{command} - {desc}\n"
            await update.message.reply_text(help_message)
