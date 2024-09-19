""" Module used to create the GUI for the application. """

import tkinter as tk
import logging
from dsb_main.dsb import DSB

class Table(tk.Frame):
    """ Class used to create a table in the application window. """
    def __init__(self, parent, columns: list, titles: list, column: int, row: int) -> None:
        super().__init__(parent)

        self.columns = columns
        self.titles = titles
        self.colors = ["red", "orange", "green"]

        for i, weight in enumerate(columns):
            self.grid_columnconfigure(i, weight=weight)
            label = tk.Label(self, text=titles[i], bd=1, relief=tk.SOLID)
            label.grid(row=0, column=i, sticky="nsew")

        self.grid(row=row, column=column, sticky="nsew")

    def add_row(self, row: int, data: list) -> None:
        """ Add a row to the table. """
        for i in range(len(self.columns)):
            try:
                text = data[i].value[0]
                color = self.colors[data[i].value[1]]
            except AttributeError:
                text = data[i]
                color = "black"

            label = tk.Label(self, text=text, fg=color, bd=1, relief=tk.SOLID)
            label.grid(row=row, column=i, sticky="nsew")

    def remove_all_rows(self) -> None:
        """ Remove all rows from the table. """
        for widget in self.winfo_children()[len(self.titles):]:
            widget.destroy()

class Logs(tk.Text): # pylint: disable=too-many-ancestors
    """ Class used to create a text field for logs. """
    def __init__(self, parent, column: int, row: int) -> None:
        super().__init__(parent, wrap=tk.WORD, height=10, width=80)
        self.insert(tk.END, "Logs will appear here.\n")
        self.config(state=tk.DISABLED)
        self.grid(row=row, column=column)

    def log(self, message: str) -> None:
        """ Log a message to the text field. """
        self.config(state=tk.NORMAL)
        self.insert(tk.END, message + "\n")
        self.config(state=tk.DISABLED)
        self.see(tk.END)

class TextHandler(logging.Handler):
    """ Custom logging handler to log messages to the Logs text field. """
    def __init__(self, logs: Logs) -> None:
        super().__init__()
        self.logs = logs

    def emit(self, record: logging.LogRecord) -> None:
        """ Emit a log message. """
        msg = self.format(record)
        self.logs.log(msg)

class App(tk.Tk):
    """ Class used to create the application window. """
    def __init__(self, bot: DSB) -> None:
        super().__init__()
        self.title("DatSimonBot")
        self.geometry("800x600")
        self.resizable(False, False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=4)
        self.grid_rowconfigure(4, weight=4)
        self.grid_columnconfigure(0, weight=1)
        self.running = False
        self.bot = bot
        self.add_widgets()
        self.bot.logger.addHandler(TextHandler(self.logs))
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update()

    def add_widgets(self) -> None:
        """ Add widgets to the application window. """
        title = tk.Label(self, text="DatSimonBot", font=("Helvetica", 20))
        title.grid(row=0, column=0)

        start_button = tk.Button(self, text="Start", command=self.run)
        start_button.grid(row=1, column=0)

        self.module_list = Table(self, [8, 2], ["Module name", "Status"], 0, 3)

        self.logs = Logs(self, 0, 4)

    def update(self) -> None:
        """ Update the application window. """
        try:
            self.module_list.remove_all_rows()

            status = self.bot.get_status()

            for i, module in enumerate(status.items()):
                self.module_list.add_row(i + 1, [module[0], module[1]])

            if not self.running:
                start_button = tk.Button(self, text="Start", command=self.run)
                start_button.grid(row=1, column=0)
            else:
                stop_button = tk.Button(self, text="Stop", command=self.stop)
                stop_button.grid(row=1, column=0)
        except (AttributeError, TypeError):
            pass
        self.after(1000, self.update)

    def run(self) -> None:
        """ Run the application. """
        self.running = True
        self.bot.run()

    def stop(self) -> None:
        """ Stop the application. """
        self.running = False
        self.bot.stop()

    def on_closing(self) -> None:
        """ Actions to perform when the window is closed. """
        if self.running:
            self.stop()
        self.destroy()

    def run_app(self) -> None:
        """ Run the application. """
        self.mainloop()
