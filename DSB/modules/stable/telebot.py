""" Telebot module. """

from DSB.modules.templates.template import Module

class Telebot(Module):
    """ Telebot instance """
    def __init__(self) -> None:
        super().__init__()
        self.name = "Telebot"