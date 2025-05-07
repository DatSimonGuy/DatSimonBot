from telegram.ext import CommandHandler
from telegram.ext.filters import User, BaseFilter

class AdminCommandHandler(CommandHandler):
    def __init__(self, dsb, command, callback, filters = None, block = ..., has_args = None):
        for admin in dsb.admins:
            if isinstance(filters, BaseFilter):
                filters = filters & User(admin)
            else:
                filters = User(admin)
        super().__init__(command, callback, filters, block, has_args)