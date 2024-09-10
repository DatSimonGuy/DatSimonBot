""" Template module for reference. """

from dsb_main.modules.base_modules.module import Module, run_only

class Template(Module):
    """ Template module for reference. """
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self._name = "Template"
        self.dependencies = ["some_dependency"]
        self._logger = None

    def some_method(self) -> None:
        """ Some method. """

    @run_only
    def some_other_method(self) -> None:
        """ Some other method. Will run only if the module is running. """
