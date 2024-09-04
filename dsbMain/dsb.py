""" Main app """

from typing import Literal
import os
import importlib
from argparse import Namespace
from dsbMain.modules.templates import template

class DSB:
    """ Main class for the application. """
    def __init__(self, modules_directory: Literal["stable", "test"]) -> None:
        self._status = {}
        self._modules: dict[str, template.Module] = {}
        self._modules_directory = modules_directory

    def import_modules(self) -> None:
        """ Imports all necessary modules. """
        for module in os.listdir("dsbMain/modules/" + self._modules_directory):
            if module.endswith(".py") and module != "__init__.py":
                module_name = module[:-3]
                module = importlib.import_module('dsbMain.modules.' +
                                                 self._modules_directory + "." + module_name)
                module_class_name = module_name.title().replace("_", "")
                module_class = getattr(module, module_class_name)
                self.add_module(module_class(self))

    def get_status(self) -> dict:
        """ Get the status of the modules. """
        for module in self._modules.values():
            self._status[module.name] = module.status
        return self._status

    def add_module(self, module: template.Module) -> None:
        """ Add a module to the application. """
        self._modules[module.name] = module
        self._status[module.name] = module.status

    def run_module(self, module_name: str, args: Namespace) -> bool:
        """ Run a module. """
        if module_name not in self._modules:
            return False

        if self._modules[module_name].running:
            return True

        self._modules[module_name].get_dependencies(args)

        return self._modules[module_name].run(args)

    def run(self, args: Namespace) -> None:
        """ Run the application. """
        for module in self._modules.values():
            self.run_module(module.name, args)

    def stop(self) -> None:
        """ Stop the application. """
        for module in self._modules.values():
            module.stop()

    def get_module(self, module_name: str) -> template.Module | None:
        """ Get a module by its name. """
        return self._modules.get(module_name, None)

    def __getitem__(self, key: str) -> template.Module:
        """ Get a module by its name. """
        return self._modules[key]

    def __contains__(self, key: str) -> bool:
        """ Check if a module is in the application. """
        return key in self._modules
