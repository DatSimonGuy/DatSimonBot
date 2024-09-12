""" Telebot help module """

from .base.base_module import BaseModule

class Help(BaseModule):
    """ Help module """
    def __init__(self, ptb, telebot_module) -> None:
        super().__init__(ptb, telebot_module)
        self._handlers = {
            "help": self._help
        }
        self.add_handlers()

    async def _help(self, update, _) -> None:
        """ Display help message """
        help_message = "Available commands:\n"
        for i, command in enumerate(self._telebot_module.commands):
            help_message += f"{i+1}. /{command}\n"
        await update.message.reply_text(help_message)
