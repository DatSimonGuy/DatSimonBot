""" Telebot mode for the GUI. """

from rich.table import Table
from rich.console import Console
from dsb_main.dsb import DSB
from .base_mode import BaseMode

class TelebotMode(BaseMode):
    """ Telebot mode for the GUI. """
    def __init__(self, bot: DSB, console: Console) -> None:
        super().__init__(bot, console)
        self.chat_table = Table()
        self.chat_info = Table()
        self._telebot = self._bot.get_module("Telebot")
        if not self._telebot:
            self._bot.log("ERROR", "Telebot module not found")
            raise ModuleNotFoundError("Telebot module not found")

    def reset_chat_table(self) -> None:
        """ Reset the chat table. """
        self.chat_table = Table(title="Chat")
        self.chat_table.grid(expand=True)
        self.chat_table.add_column("User", style="cyan")
        self.chat_table.add_column("Message", style="magenta", width=40)

    def reset_chat_info(self) -> None:
        """ Reset the chat info table. """
        self.chat_info = Table(title="Chat info")
        self.chat_info.grid(expand=True)
        self.chat_info.add_column("Group_id", style="cyan")
        self.chat_info.add_column("Group_name", style="magenta")
        self.chat_info.add_column("Group description", style="green")

    def display(self) -> None:
        """ Display the telebot mode. """
        self._console.clear()
        self.reset_chat_table()
        self.reset_chat_info()
        self._console.print(self.chat_info)
        self._console.print(self.chat_table)
