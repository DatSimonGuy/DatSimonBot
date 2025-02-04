""" Module for data transformations """

from datetime import datetime, time
from typing import Optional

def to_index(value: str | int) -> Optional[int]:
    """ Get integer from string """
    if isinstance(value, int):
        return value
    if not value.isdigit():
        return None
    return int(value)

def str_to_day(string: str) -> Optional[int]:
    """ Convert string to a valid day value """
    if string.isdigit():
        day = int(string)
        if day not in range(1, 6):
            return None
        return day
    days = {
        "monday": 1,
        "tuesday": 2,
        "wednesday": 3,
        "thursday": 4,
        "friday": 5
    }
    day = days.get(string.lower(), None)
    return day

def str_to_time(string: str) -> time:
    """ Get valid datetime.time from string """
    try:
        return datetime.strptime(string, "%H:%M").time()
    except Exception: #pylint: disable=broad-exception-caught
        return None
