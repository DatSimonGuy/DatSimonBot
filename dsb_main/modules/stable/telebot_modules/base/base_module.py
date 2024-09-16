""" telegram bot base module """

from telegram.ext import CommandHandler

def admin_only(func):
    """ Decorator for admin only commands """
    async def wrapper(self, update, context):
        """ Wrapper function """
        if str(update.effective_user.id) in self.config.get("admins", []):
            await func(self, update, context)
        else:
            await update.message.reply_text("You are not an admin")
    return wrapper

def prevent_edited(func):
    """ Decorator for commands that won't work on edited messages """
    async def wrapper(self, update, context):
        """ Wrapper function """
        if update.edited_message:
            return
        await func(self, update, context)
    return wrapper

class BaseModule:
    """ Base module for all telegram bot modules. """
    def __init__(self, bot, telebot_module) -> None:
        self._ptb = bot
        self._handlers = {}
        self._telebot_module = telebot_module

    @property
    def handlers(self) -> dict:
        """ Get the handlers """
        return self._handlers

    @property
    def config(self) -> dict:
        """ Get the bot configuration """
        return self._telebot_module.config

    def add_handlers(self) -> None:
        """ Add handlers to the dispatcher """
        for command, handler in self._handlers.items():
            self._ptb.add_handler(CommandHandler(command, handler))

    def remove_handlers(self) -> None:
        """ Remove handlers from the dispatcher """
        for command, handler in self._handlers.items():
            self._ptb.remove_handler(CommandHandler(command, handler))

    def _get_args(self, context) -> tuple[list, dict]:
        """ Get the command arguments and options """
        args = []
        kwargs = {}
        current = ""
        for arg in context.args:
            if arg.startswith("-"):
                current = arg[1:]
            elif current in kwargs:
                kwargs[current] += " " + arg
            else:
                kwargs[current] = arg
            if current == "":
                args.append(arg)
        return args, kwargs
