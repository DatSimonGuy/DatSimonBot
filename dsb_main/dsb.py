""" Main app """

import os
import importlib
from argparse import Namespace
import dotenv
from dsb_main.modules.base_modules import module

class DSB:
    """ Main class for the application. """
    def __init__(self, args: Namespace) -> None:
        self._modules: dict[str, module.Module] = {}
        self._modules_directory = "experimental" if args.experimental else "stable"
        self.config = dotenv.dotenv_values("dsb_main/.env")
        self._import_modules()

    def _import_modules(self) -> None:
        """ Imports all necessary modules. """
        for module_name in os.listdir("dsb_main/modules/" + self._modules_directory):
            if module_name.endswith(".py") and module_name != "__init__.py":
                module_name = module_name[:-3]
                loaded_module = importlib.import_module('dsb_main.modules.' +
                                                 self._modules_directory + "." + module_name)
                module_class_name = module_name.title().replace("_", "")
                module_class = getattr(loaded_module, module_class_name)
                self.add_module(module_class(self))

    def get_status(self) -> dict:
        """ Get the status of the modules. """
        status = {}
        for module_info in self._modules.values():
            status[module_info.name] = module_info.status
        return status

    def add_module(self, new_module: module.Module) -> None:
        """ Add a module to the application. """
        self._modules[new_module.name] = new_module

    def _run_module(self, module_name: str) -> bool:
        """ Run a module. """
        if module_name not in self._modules:
            return False

        if self._modules[module_name].running:
            return True

        dependencies = self._modules[module_name].dependencies

        for dependency in dependencies:
            if not self._run_module(dependency):
                return False

        return self._modules[module_name].run()

    def run(self) -> None:
        """ Run the application. """
        for current_module in self._modules.values():
            self._run_module(current_module.name)

    def stop(self) -> None:
        """ Stop the application. """
        for current_module in self._modules.values():
            if current_module.running:
                current_module.stop()

    def get_module(self, module_name: str) -> module.Module | None:
        """ Get a module by its name. """
        return self._modules.get(module_name, None)

    def __getitem__(self, key: str) -> module.Module:
        """ Get a module by its name. """
        return self._modules[key]

    def __contains__(self, key: str) -> bool:
        """ Check if a module is in the application. """
        return key in self._modules
