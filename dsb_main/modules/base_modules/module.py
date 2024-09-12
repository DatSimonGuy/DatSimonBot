""" Base module to use as a base for creating new modules. """

from dsb_main.modules.base_modules.statuses import Status

def run_only(func):
    """ Decorator used to run a function only if the module is running. """
    def wrapper(self, *args, **kwargs):
        if self.running:
            return func(self, *args, **kwargs)
        return None
    return wrapper

class Module:
    """ Class used to create new modules. It needs to be named as the file
    using PascalCase for importing purposes."""
    def __init__(self, bot) -> None:
        self._name = "Module"
        self._status = Status.NOT_RUNNING
        self.dependencies = [] # List of module names that this module depends on
        self._bot = bot

    @property
    def name(self) -> str:
        """ Get the name of the module. """
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """ Set the name of the module. """
        self._name = new_name

    @property
    def status(self) -> Status:
        """ Get the status of the module. """
        return self._status

    @status.setter
    def status(self, status: Status) -> None:
        """ Set the status of the module. """
        self._status = status

    @property
    def running(self) -> bool:
        """ Check if the module is running. """
        return self._status == Status.RUNNING

    def add_dependency(self, module_name: str) -> None:
        """ Add a dependency to the module. """
        self.dependencies.append(module_name)

    def run(self) -> bool:
        """ Run the module. """
        self._status = Status.RUNNING
        return True

    def stop(self) -> None:
        """ Stop the module. """
        self._status = Status.NOT_RUNNING
