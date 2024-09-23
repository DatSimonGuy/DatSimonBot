""" CLI GUI for the application. """

from rich.console import Console
from dsb_main.dsb import DSB
from .modes.app_mode import AppMode
from .modes.telebot_mode import TelebotMode
from .modes.base_mode import BaseMode

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
            "switch_mode": self.switch_mode,
        }
        self._mode_types = {
            "app": AppMode,
            "telebot": TelebotMode,
        }
        self._modes = {}
        for name, mode in self._mode_types.items():
            try:
                self.add_mode(mode(bot, self._console), name)
            except ModuleNotFoundError:
                pass
        self._mode = self._modes["app"]

    def add_mode(self, mode: BaseMode, name: str) -> None:
        """ Add a new mode to the application. """
        self._modes[name] = mode

    def update(self) -> None:
        """ Update the application window. """
        try:
            self._console.clear()
            self._mode.display()
            user_input = input("Enter command: ")
            if user_input in self._commands:
                self._commands[user_input]()
            elif user_input in self._mode.commands:
                self._mode.commands[user_input]()
            else:
                print("Unknown command")
                input("Press enter to continue")
        except (AttributeError, TypeError):
            pass

    def get_commands(self) -> None:
        """ Get the available commands. """
        self._console.clear()
        help_text = "Available commands:\n"
        functions = set()
        commands = self._mode.commands
        commands.update(self._commands)
        for func in commands.values():
            if func.__name__ not in functions:
                help_text += ", ".join(command for command, function in commands.items() \
                    if function == func)
                help_text += f" - {func.__doc__}\n"
                functions.add(func.__name__)
        print(help_text)
        input("Press enter to continue")

    def switch_mode(self) -> None:
        """ Switch the application mode. """
        if not self._bot.running:
            print("The bot is not running, please start the bot first")
            input("Press enter to continue")
            return
        print("Available modes:")
        for mode in self._modes:
            print(mode)
        mode = input("Enter mode: ")
        if mode in self._modes:
            self._mode = self._modes[mode]
        else:
            print("Unknown mode")
            input("Press enter to continue")

    def start(self) -> None:
        """ Start the application. """
        try:
            self._bot.run()
        except Exception as e: # pylint: disable=broad-except
            print(f"An error occurred: {e}")
            input("Press enter to continue")
        while self.running:
            try:
                self.update()
            except KeyboardInterrupt:
                self.stop_app()
                break

    def stop_app(self) -> None:
        """ Stop the application. """
        self.running = False
        self._bot.stop()

    def run_app(self) -> None:
        """ Run the application. """
        self.running = True
        self.start()
