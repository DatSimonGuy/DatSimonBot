""" Telebot help module """

from .base_module.base_module import BaseModule

class Help(BaseModule):
    """ Help module """
    def __init__(self, ptb) -> None:
        super().__init__(ptb)
        self._handlers = {
            "help": self._help
        }
        self.add_handlers()

    async def _help(self, update, _) -> None:
        """ Display help message """
        await update.message.reply_text("This is a help message")
