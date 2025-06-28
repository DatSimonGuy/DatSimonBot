
import re
import enum

class HandlerType(enum.Enum):
    DEFAULT = 0
    ADMIN_ONLY = 1
    BOT_ADMIN = 2
    CALLBACK = 3
    INLINE = 4

def command(command_name: str):
    """ Default command decorator """
    def decorator(func):
        func._command_name = command_name
        func._handler_type = HandlerType.DEFAULT
        help_message = re.search(r"<HELP>.*<HELP>", func.__doc__)
        if help_message is not None:
            help_message = help_message.replace("<HELP>", "")
        func._help = help_message
    return decorator

def admin_command(command_name: str):
    """ Command only for admins of the group chat """
    def decorator(func):
        func._command_name = command_name
        func._handler_type = HandlerType.ADMIN_ONLY
        help_message = re.search(r"<HELP>.*<HELP>", func.__doc__)
        if help_message is not None:
            help_message = help_message.replace("<HELP>", "")
            help_message = f"This command is avaible only to admins of this groupchat\n{help_message}"
        func._help = help_message
    return decorator

def system_command(command_name: str):
    """ Command only for bot admins """
    def decorator(func):
        func._command_name = command_name
        func._handler_type = HandlerType.BOT_ADMIN
        help_message = re.search(r"<HELP>.*<HELP>", func.__doc__)
        if help_message is not None:
            help_message = help_message.replace("<HELP>", "")
        func._help = help_message
    return decorator

def callback_handler(command_name: str):
    def decorator(func):
        func._command_name = command_name
        func._handler_type = HandlerType.CALLBACK
    return decorator

class BaseModule:
    """ Base module class, every dsb module needs to inherit from it """
    def __init__(self):
        pass