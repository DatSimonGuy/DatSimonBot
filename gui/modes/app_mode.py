""" App mode for cli gui. """

from logging import Handler
import rich.progress
from rich.console import Console
from rich.columns import Columns
from rich.table import Table
from dsb_main.dsb import DSB
from .base_mode import BaseMode

class TextHandler(Handler):
    """ Custom logging handler to log messages to the Logs text field. """
    def __init__(self, app: 'AppMode') -> None:
        super().__init__()
        self.app = app

    def emit(self, record) -> None:
        """ Emit a log record. """
        self.app.log(record.asctime, record.levelname, record.msg)

class AppMode(BaseMode):
    """ Class used to create the application window. """
    def __init__(self, bot: DSB, console: Console) -> None:
        super().__init__(bot, console)
        bot.logger.addHandler(TextHandler(self))
        self._status_table = Table()
        self._logs_table = Table()
        self._logs = []
        self._commands = {
            "start": self._bot.run,
            "stop": self.stop_bot,
            "restart": self.restart_bot,
            "r": self.restart_bot,
        }

    @property
    def commands(self) -> dict:
        """ Returns the list of commands. """
        return self._commands

    def display(self) -> None:
        """ Display the application window. """
        self._console.clear()
        self.reset_status_table()
        self.reset_logs_table()
        self._console.print(Columns([self._status_table, self._logs_table]))

    def reset_status_table(self) -> None:
        """ Reset the table. """
        self._status_table = Table(title="Module status")
        self._status_table.grid(expand=True)
        self._status_table.add_column("Module name", style="cyan")
        self._status_table.add_column("Status", style="magenta")
        self._status_table.add_column("Description", style="green")
        status = self._bot.get_status()
        for module in status.items():
            self._status_table.add_row(module[0], module[1].value[0],
                                       self._bot.get_module(module[0]).__doc__)

    def reset_logs_table(self) -> None:
        """ Reset the logs table. """
        self._logs_table = Table(title="Logs")
        self._logs_table.grid(expand=True)
        self._logs_table.add_column("Time", style="cyan")
        self._logs_table.add_column("Level", style="magenta")
        self._logs_table.add_column("Message", style="green")
        for log in self._logs[-10:]:
            self._logs_table.add_row(log[0], log[1], log[2])
        if len(self._logs) < 10:
            for _ in range(10 - len(self._logs)):
                self._logs_table.add_row("", "", "")

    def log(self, time: str, level: str, message: str) -> None:
        """ Log a message. """
        self._logs.append((time, level, message))

    def stop_bot(self) -> None:
        """ Stop the bot. """
        with rich.progress.Progress(console=self._console) as progress:
            task = progress.add_task("Stopping bot...", total=self._bot.module_ammount)
            for module in self._bot.get_modules():
                progress.update(task, advance=1, description=f"Stopping {module.name}")
                if module.running:
                    try:
                        module.stop()
                    except Exception as exc: # pylint: disable=broad-except
                        self._bot.log("ERROR", f"Error stopping module {module.name}", exc_info=exc)

    def restart_bot(self) -> None:
        """ Restart the bot. """
        self.stop_bot()
        self._bot.run()
        