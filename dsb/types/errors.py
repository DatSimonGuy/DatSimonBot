""" Base error class for dsb """

class DSBError(Exception):
    """ Base error class for dsb """

class InvalidValueError(DSBError):
    """ Raised when invalid parameter is provided """
    def __init__(self, parameter: str, *args) -> None:
        super().__init__(f"Please provide valid {parameter} value", *args)
