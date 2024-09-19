""" Main app """

import os
import importlib
import logging
from typing import Literal, TYPE_CHECKING, Optional
from argparse import Namespace
import dotenv
from dsb_main.modules.base_modules.statuses import Status
if TYPE_CHECKING:
    from dsb_main.modules.base_modules.module import Module

class DSB:
    """ Main class for the application. """
    def __init__(self, args: Namespace) -> None:
        self._modules: dict[str, 'Module'] = {}
        self._experimental = args.experimental
        self.config = dotenv.dotenv_values("dsb_main/.env")
        self._logger = logging.getLogger("DSB")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler("dsb_main/dsb.log")
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        for arg in vars(args):
            self.config[arg] = getattr(args, arg)
        self._import_modules()

    @property
    def logger(self) -> logging.Logger:
        """ Get the logger. """
        return self._logger

    def set_log_level(self, level: Literal["ERROR", "INFO", "WARNING", "DEBUG"]) -> None:
        """ Set the log level. """
        levels = {
            "ERROR": logging.ERROR,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "DEBUG": logging.DEBUG
        }
        self._logger.setLevel(levels.get(level, logging.INFO))

    def _import_modules(self, reload: bool = False) -> None:
        """ Imports or reloads all necessary modules. """
        e_modules = os.listdir("dsb_main/modules/experimental") if self._experimental else []
        s_modules = os.listdir("dsb_main/modules/stable")
        for module_name in e_modules + s_modules:
            if module_name in self._modules:
                continue
            if module_name.endswith(".py") and module_name != "__init__.py":
                module_name = module_name[:-3]
                if reload:
                    loaded_module = importlib.reload(importlib.import_module(
                        'dsb_main.modules.stable' + "." + module_name))
                else:
                    loaded_module = importlib.import_module(
                        'dsb_main.modules.stable' + "." + module_name)
                module_class_name = module_name.title().replace("_", "")
                module_class: 'Module' = getattr(loaded_module, module_class_name)
                try:
                    module = module_class(self)
                    self.add_module(module)
                except Exception as exc: # pylint: disable=broad-except
                    self._logger.error("Error loading module %s", module_name, exc_info=exc)
                    if module_class.name in self._modules:
                        self._modules[module_class.name].status = Status.ERROR

    def get_status(self) -> dict:
        """ Get the status of the modules. """
        status = {}
        for module_info in self._modules.values():
            status[module_info.name] = module_info.status
        return status

    def add_module(self, new_module: 'Module') -> None:
        """ Add a module to the application. """
        self._modules[new_module.name] = new_module

    def _run_module(self, module_name: str) -> bool:
        """ Run a module. """
        try:
            if self._modules[module_name].error:
                return False
            return self._modules[module_name].run()
        except Exception as exc: # pylint: disable=broad-except
            self._logger.error("Error running module %s", module_name, exc_info=exc)
            return False

    def run(self) -> None:
        """ Run the application. """
        self._import_modules(reload=True)
        for current_module in self._modules.values():
            if not self._run_module(current_module.name):
                self._modules[current_module.name].status = Status.ERROR

    def stop(self) -> None:
        """ Stop the application. """
        for module in self._modules.values():
            if module.running:
                try:
                    module.stop()
                except Exception as exc: # pylint: disable=broad-except
                    self._logger.error("Error stopping module %s", module.name, exc_info=exc)

    def get_module(self, module_name: str) -> Optional['Module']:
        """ Get a module by its name. """
        return self._modules.get(module_name, None)

    def log(self, level: Literal["ERROR", "INFO", "WARNING", "DEBUG"],
            message: str, exc_info: Optional[Exception] = None) -> None:
        """ Log a message. """
        levels = {
            "ERROR": logging.ERROR,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "DEBUG": logging.DEBUG
        }
        self._logger.log(levels.get(level, logging.INFO), message, exc_info=exc_info)
