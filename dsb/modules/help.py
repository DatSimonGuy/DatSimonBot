""" Telebot help module """

from telegram import Update
from telegram.ext import ContextTypes, Application
from dsb.types.module import BaseModule
from dsb.old_dsb import DSB

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
        """
        Display help message.
        
        Usage: /help <command> [--botfather]

        -----------
        Format used (without argument):
        - /command - Description
        - /command2 - Description2
        ...
        -----------
        Format used (with argument):
        Description of the command.
        
        Usage: /command <arg1> <arg2> ...
        
        Explaination of parameters:
        - arg1 : type
            Description of the first argument.
        - arg2 : type
            Description of the second argument.
        -----------
        
        Symbols:
        - <value_name> : required value, 
        for example: /command <age> means you should do /command 18

        - --arg_name : required named argument, everything after it is taken as its value, 
        for example: /command --name <name> means you should do /command --name John

        - [--arg_name] : Optional named argument, does not need to be given value, 
        for example: /command [optional_arg] means you can do /command or /command --optional_arg

        - [--arg_name <arg_value>] : Optional named argument, requires value,
        for example: /command [surname <surname>] means you can do /command or /command --surname 18

        - () : Specifies actions required for the command to work, 
        for example: /command (Please reply to a message)

        Command parameters
        -----------
        command : text
            The command to display help for.
        botfather : No value (Optional)
            If added, display all commands in botfather compatible format, ignores command arg.
        """
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
