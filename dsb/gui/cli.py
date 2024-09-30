""" Command line interface for the bot. """

from logging import Handler
import rich.progress
from rich.prompt import Prompt
import rich.live
from rich.table import Table
from rich.console import Console
from rich.columns import Columns
from dsb.main.dsb_class import DSB

class TextHandler(Handler):
    """ Custom logging handler to log messages to the Logs text field. """
    def __init__(self, app: 'App') -> None:
        super().__init__()
        self.app = app

    def emit(self, record) -> None:
        """ Emit a log record. """
        self.app.log(record.asctime, record.levelname, record.msg)

class App:
    """ Class used to create the application window. """
    def __init__(self, bot: DSB) -> None:
        self.running = False
        self._bot = bot
        self._console = Console()
        self._commands = {
            "quit": self.stop_app,
            "exit": self.stop_app,
            "q": self.stop_app,
            "commands": self.get_commands,
            "help": self.get_commands,
            "start": self.start,
            "stop": self.stop_bot,
            "restart": self.restart_bot,
            "r": self.restart_bot,
            "database": self.show_database,
            "send": self.send_message,
            "add_chat_macro": self.add_chat_macro,
            "remove_chat_macro": self.remove_chat_macro
        }
        bot.logger.addHandler(TextHandler(self))
        self._status_table = Table()
        self._logs_table = Table()
        self._logs = []

    def display(self) -> Columns:
        """ Display the application window. """
        self.reset_status_table()
        self.reset_logs_table()
        return Columns([self._status_table, self._logs_table])

    def command_prompt(self) -> None:
        """ Command prompt for user input with hints. """
        command = Prompt.ask("Enter command", choices=list(self._commands.keys()),
                             show_choices=False, case_sensitive=False)
        if command in self._commands:
            self._commands[command]()

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

    def log(self, timestamp: str, level: str, message: str) -> None:
        """ Log a message. """
        self._logs.append((timestamp, level, message))

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

    def update(self) -> None:
        """ Update the application window. """
        try:
            while self.running:
                self._console.clear()
                columns = self.display()
                self._console.print(columns)
                self.command_prompt()
        except KeyboardInterrupt:
            self.stop_app()
        except EOFError:
            self.stop_app()
        except (AttributeError, TypeError):
            pass

    def show_database(self) -> None:
        """ Show the database directory tree. """
        self._console.clear()
        database = self._bot.get_module("Database")
        if not database:
            self._console.print("Database module not found")
            return
        data = database.tree()
        self._console.print(data)
        input("Press enter to continue")

    def send_message(self) -> None:
        """ Send a message to a chat. """
        telebot = self._bot.get_module("Telebot")
        if not telebot:
            self._console.print("Telebot module not found")
            return
        message_handler = telebot.get_telebot_module("MessageHandler")
        chat_id = input("Enter chat id: ")
        if message_handler:
            macros = telebot.chat_macros
            if chat_id in macros:
                chat_id = macros[chat_id]
            self._console.clear()
            message_table = Table(title="Last messages")
            message_table.add_column("Message", style="cyan")
            message_table.add_column("Sender", style="magenta")
            message_table.add_column("Time", style="green")
            for message in message_handler.messages.get(int(chat_id), []):
                message_table.add_row(message.text, message.from_user.username,
                                      message.date.strftime("%H:%M"))
            self._console.print(message_table)
        message = input("Enter message: ")
        if message:
            telebot.send_message(chat_id, message)

    def add_chat_macro(self) -> None:
        """ Add a chat macro. """
        chat_id = input("Enter chat id: ")
        macro = input("Enter macro: ")
        telebot = self._bot.get_module("Telebot")
        if not telebot:
            self._console.print("Telebot module not found")
            return
        telebot.add_chat_macro(chat_id, macro)

    def remove_chat_macro(self) -> None:
        """ Remove a chat macro. """
        macro = input("Enter macro: ")
        telebot = self._bot.get_module("Telebot")
        if not telebot:
            self._console.print("Telebot module not found")
            return
        telebot.remove_chat_macro(macro)

    def get_commands(self) -> None:
        """ Get the available commands. """
        self._console.clear()
        commands_table = Table(title="Available Commands")
        commands_table.add_column("Command", style="cyan")
        commands_table.add_column("Description", style="green")

        functions = set()
        for function in self._commands.values():
            if function not in functions:
                functions.add(function)
                commands = ", ".join(command for command,
                                    func in self._commands.items() if func == function) # pylint: disable=comparison-with-callable
                description = function.__doc__ or "No description available"
                commands_table.add_row(commands, description)

        self._console.print(commands_table)
        input("Press enter to continue")

    def start(self) -> None:
        """ Start the application. """
        try:
            self._bot.run()
        except Exception as e: # pylint: disable=broad-except
            print(f"An error occurred: {e}")
            input("Press enter to continue")
        self.running = True
        self.update()

    def stop_app(self) -> None:
        """ Stop the application. """
        self.running = False
        self._bot.stop()

    def run_app(self) -> None:
        """ Run the application. """
        self.running = True
        self.start()
