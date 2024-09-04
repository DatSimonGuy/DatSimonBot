""" Module used to create the GUI for the application. """

from datetime import datetime
import tkinter as tk
from argparse import Namespace

class Table(tk.Frame):
    """ Class used to create a table in the application window. """
    def __init__(self, parent, columns: list, titles: list, column: int, row: int) -> None:
        super().__init__(parent)

        self.columns = columns
        self.titles = titles
        self.COLORS = ["red", "orange", "green"]

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
                color = self.COLORS[data[i].value[1]]
            except AttributeError:
                text = data[i]
                color = "black"

            label = tk.Label(self, text=text, fg=color, bd=1, relief=tk.SOLID)
            label.grid(row=row, column=i, sticky="nsew")

class Logs(tk.Text):
    """ Class used to create a text field for logs. """
    def __init__(self, parent, column: int, row: int) -> None:
        super().__init__(parent, wrap=tk.WORD, height=10, width=80)
        self.insert(tk.END, "Logs will appear here.\n")
        self.config(state=tk.DISABLED)
        self.grid(row=row, column=column)
    
    def log(self, message: str) -> None:
        """ Log a message to the text field. """
        self.config(state=tk.NORMAL)
        self.insert(tk.END, datetime.now().strftime("%d/%m %H:%M") + " " + message + "\n")
        self.config(state=tk.DISABLED)
        self.see(tk.END)

class App(tk.Tk):
    """ Class used to create the application window. """
    def __init__(self) -> None:
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
        self.add_widgets()
        self.update()

    def set_functions(self, run_function, stop_function, args: Namespace, status_function) -> None:
        """ Set the functions for the application. """
        self.run_func = run_function
        self.stop_func = stop_function
        self.args = args
        self.get_status = status_function

    def add_widgets(self) -> None:
        """ Add widgets to the application window. """
        title = tk.Label(self, text="DatSimonBot", font=("Helvetica", 20))
        title.grid(row=0, column=0)

        start_button = tk.Button(self, text="Start", command=lambda: self.run(self.args))
        start_button.grid(row=1, column=0)

        self.module_list = Table(self, [8, 2], ["Module name", "Status"], 0, 3)

        self.logs = Logs(self, 0, 4)

    def update(self) -> None:
        """ Update the application window. """
        try:
            status = self.get_status()
            for i, module in enumerate(status.items()):
                self.module_list.add_row(i + 1, [module[0], module[1]])
            if not self.running:
                start_button = tk.Button(self, text="Start", command=lambda: self.run(self.args))
                start_button.grid(row=1, column=0)
            else:
                stop_button = tk.Button(self, text="Stop", command=self.stop)
                stop_button.grid(row=1, column=0)
        except AttributeError:
            pass
        self.after(1000, self.update)

    def run(self, args: Namespace) -> None:
        """ Run the application. """
        self.running = True
        self.run_func(args)

    def stop(self) -> None:
        """ Stop the application. """
        self.running = False
        self.stop_func()

    def log(self, message: str) -> None:
        """ Log a message to the text field. """
        self.logs.log(message)

    def run_app(self) -> None:
        """ Run the application. """
        self.mainloop()
