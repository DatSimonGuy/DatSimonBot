""" telegram bot base module """

import functools
from typing import TYPE_CHECKING
from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes, CallbackQueryHandler, \
    InlineQueryHandler
if TYPE_CHECKING:
    from dsb.engine import DSBEngine

def admin_only(func):
    """ Decorator for admin only commands """
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Wrapper function """
        if update.effective_user.id in self._dsb.admins:
            await func(self, update, context)
        else:
            await update.message.reply_text("You are not an admin")
    return wrapper

def prevent_edited(func):
    """ Decorator for commands that won't work on edited messages """
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Wrapper function """
        if update.edited_message:
            return
        await func(self, update, context)
    return wrapper

def callback_handler(func):
    """ Decorator for callback query handlers """
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Wrapper function """
        if update.effective_user.id != int(update.callback_query.data.split(":")[-1]):
                return
        if update.callback_query.data.split(":")[-2] == "cancel":
            await context.bot.delete_message(chat_id=update.effective_chat.id,
                                       message_id=update.effective_message.id)
            return
        await func(self, update, context)
    return wrapper

class BaseModule:
    """ Base module for all telegram bot modules. """
    def __init__(self, bot: Application, dsb: 'DSBEngine') -> None:
        self._bot = bot
        self._handlers = {}
        self._descriptions = {}
        self._callback_handlers = {}
        self._inline_handlers = {}
        self._dsb = dsb
        self._handler_list = []

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
        return self._dsb.config

    async def _like(self, update: Update) -> None:
        """ React to message with thumbs up """
        await update.message.set_reaction("👍")

    async def _reply_t(self, update: Update, message: str) -> None:
        """ Reply to message with text """
        if len(message) == 0:
            return
        await update.message.reply_text(message)

    def prep(self) -> None:
        """ Prepare the module """

    def add_handlers(self) -> None:
        """ Add handlers to the dispatcher """
        for command, handler in self._handlers.items():
            handler = CommandHandler(command, handler)
            self._handler_list.append(handler)
            self._bot.add_handler(handler)
        for pattern, handler in self._callback_handlers.items():
            handler = CallbackQueryHandler(handler, pattern=pattern)
            self._handler_list.append(handler)
            self._bot.add_handler(handler)
        for command, handler in self._inline_handlers.items():
            handler = InlineQueryHandler(handler, pattern=command)
            self._handler_list.append(handler)
            self._bot.add_handler(handler)

    def remove_handlers(self) -> None:
        """ Remove handlers from the dispatcher """
        for handler in self._handler_list:
            try:
                self._bot.remove_handler(handler)
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
