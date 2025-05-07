""" telegram bot base module """

import os
import functools
from typing import TYPE_CHECKING
from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes, CallbackQueryHandler, \
    InlineQueryHandler, InvalidCallbackData
from dsb.utils.button_picker import CallbackData
from dsb.types.errors import DSBError
if TYPE_CHECKING:
    from dsb.dsb import DSB

def admin_only(func):
    """ Decorator for admin only commands """
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Wrapper function """
        if update.effective_user.id in self._dsb.admins: # pylint: disable=protected-access
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
        if isinstance(update.callback_query.data, InvalidCallbackData):
            await update.effective_message.delete()
            await update.callback_query.answer(text="This request was too old", show_alert=True)
            return
        callback : CallbackData = update.callback_query.data[1]
        if update.effective_user.id != callback.caller:
            return
        if callback.data.get("cancel", False):
            await context.bot.delete_message(chat_id=update.effective_chat.id,
                                       message_id=update.effective_message.id)
            return
        await func(self, update, context)
    return wrapper

class BaseModule:
    """ Base module for all telegram bot modules. """
    def __init__(self, bot: Application, dsb: 'DSB') -> None:
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

    def save_file(self, file: bytes, path: str) -> None:
        """ Save a file """
        os.makedirs(os.path.join(self._dsb.config["database_path"],
                                 os.path.dirname(path)), exist_ok=True)
        with open(path, "wb") as file_:
            file_.write(file)

    def load_file(self, path: str) -> bytes:
        """ Load a file """
        try:
            with open(os.path.join(self._dsb.config["database_path"], path), "rb") as file:
                return file.read()
        except FileNotFoundError:
            return b""

    def prep(self) -> None:
        """ Prepare the module """

    def add_handlers(self) -> None:
        """ Add handlers to the dispatcher """
        for command, handler in self._handlers.items():
            handler = CommandHandler(command, handler)
            self._handler_list.append(handler)
            self._bot.add_handler(handler)
        for func, handler in self._callback_handlers.items():
            handler = CallbackQueryHandler(
                handler,
                pattern=lambda x, func=func: isinstance(x, InvalidCallbackData) \
                    or x[1].prefix == func
            )
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

    def _parse_command(self, context: ContextTypes.DEFAULT_TYPE,
                       required_args: dict[str, type] | None = None,
                       optional_args: dict[str, type] | None = None,
                       default_arg_type: type = str) -> dict:
        """ Parse the command arguments 

        Args:
            context (ContextTypes.DEFAULT_TYPE): update context
            required_args (dict[str, type]): dictionary of required arguments and their types
            required_args (dict[str, type]): dictionary of optional arguments and their types
            default_arg (type, optional): The type of the unnamed argument after the command. Defaults to str.

        Returns:
            dict: dict of parsed argument values.
        
        Raises:
            DSBError: When there's a missing argument or the argument type does not match
        """
        argstr = str(" ".join(context.args))
        argstr = argstr.replace("—", "--")
        args = argstr.split("--")
        data = {}
        try:
            default = default_arg_type(args[0].strip())
            data["0"] = default
        except TypeError:
            raise DSBError(f"The first argument should be of type {str(default_arg_type)}")
        for arg in args[1:]:
            arg = arg.split(maxsplit=1)
            if len(arg) == 1:
                name, value = arg[0], arg[0]
            else:
                name, value = arg
            data[name] = value.strip()

        if required_args:
            self.__validate_required_args(required_args, data)

        if optional_args:
            self.__validate_optional_arguments(optional_args, data)

        return data

    def __validate_optional_arguments(self, optional_args, data):
        invalid_types = []
        for arg in optional_args:
            try:
                data[arg] = optional_args[arg](data[arg])
            except ValueError:
                invalid_types.append((arg, optional_args[arg]))
        if len(invalid_types) > 0:
            error_message = "\n".join(f"Invalid type of {arg}, should be {t}"
                                           for arg, t in invalid_types)
            raise DSBError(error_message)

    def __validate_required_args(self, required_args, data):
        missing_args = []
        invalid_types = []
        for arg in required_args:
            if arg not in data:
                missing_args.append(arg)
                continue
            try:
                data[arg] = required_args[arg](data[arg])
            except ValueError:
                invalid_types.append((arg, required_args[arg]))
        error_message = ""
        if len(missing_args) > 0:
            error_message += "\n".join(f"Missing argument {arg}" for arg in missing_args)
            error_message += "\n"
        if len(invalid_types) > 0:
            error_message += "\n".join(f"Invalid type of {arg}, should be {t}"
                                           for arg, t in invalid_types)
        if len(error_message) > 0:
            raise DSBError(error_message)

    def prepare(self) -> bool:
        """ Prepare the module """
        return True
