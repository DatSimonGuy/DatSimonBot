""" telegram bot base module """

from typing import TYPE_CHECKING
from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes
if TYPE_CHECKING:
    from telebot.telebot_module import Telebot

def admin_only(func):
    """ Decorator for admin only commands """
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Wrapper function """
        if str(update.effective_user.id) in self.config.get("admins", []):
            await func(self, update, context)
        else:
            await update.message.reply_text("You are not an admin")
    return wrapper

def prevent_edited(func):
    """ Decorator for commands that won't work on edited messages """
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Wrapper function """
        if update.edited_message:
            return
        await func(self, update, context)
    return wrapper

class BaseModule:
    """ Base module for all telegram bot modules. """
    def __init__(self, bot: Application, telebot_module: 'Telebot') -> None:
        self._ptb = bot
        self._handlers = {}
        self._descriptions = {}
        self._telebot_module = telebot_module

    @property
    def handlers(self) -> dict:
        """ Get the handlers """
        return self._handlers

    @property
    def descriptions(self) -> dict:
        """ Get the command descriptions """
        return self._descriptions

    @property
    def config(self) -> dict:
        """ Get the bot configuration """
        return self._telebot_module.config

    def prep(self) -> None:
        """ Prepare the module """

    def add_handlers(self) -> None:
        """ Add handlers to the dispatcher """
        for command, handler in self._handlers.items():
            self._ptb.add_handler(CommandHandler(command, handler))

    def remove_handlers(self) -> None:
        """ Remove handlers from the dispatcher """
        for command, handler in self._handlers.items():
            try:
                self._ptb.remove_handler(CommandHandler(command, handler))
            except ValueError:
                pass

    def _get_args(self, context: ContextTypes.DEFAULT_TYPE) -> tuple[list, dict]:
        """ Get the command arguments and options """
        args = []
        kwargs = {}
        current = ""
        for arg in context.args:
            if arg.startswith(("--", "—")):
                if current and current not in kwargs:
                    kwargs[current] = True
                current = arg.lstrip("--").lstrip("—")
            elif current in kwargs:
                kwargs[current] += " " + arg
            elif current:
                kwargs[current] = arg
            else:
                args.append(arg)
        if current and current not in kwargs:
            kwargs[current] = True
        return args, kwargs

    def prepare(self) -> bool:
        """ Prepare the module """
        return True
