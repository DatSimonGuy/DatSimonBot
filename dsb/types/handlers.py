from telegram.ext import CommandHandler
from telegram.ext.filters import User, BaseFilter, UpdateType

class DSBCommandHandler(CommandHandler):
    def __init__(self, command, callback, filters = None, block = ..., has_args = None):
        if isinstance(filters, BaseFilter):
            filters = filters & ~UpdateType.EDITED_MESSAGE
        else:
            filters = ~UpdateType.EDITED_MESSAGE
        super().__init__(command, callback, filters, block, has_args)

class AdminCommandHandler(DSBCommandHandler):
    def __init__(self, dsb, command, callback, filters = None, block = ..., has_args = None):
        for admin in dsb.admins:
            if isinstance(filters, BaseFilter):
                filters = filters & User(admin)
            else:
                filters = User(admin)
        super().__init__(command, callback, filters, block, has_args)