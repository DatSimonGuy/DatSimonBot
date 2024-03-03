from datetime import date, time
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

def ToDate(string) -> date:
    try:
        params = string.split(".")
        day = int(params[0])
        month = int(params[1])
        year = int(params[2])
        return date(year, month, day)
    except (ValueError, IndexError):
        return None


def ToTime(string) -> time:
    try:
        params = string.split(":")
        hour = int(params[0])
        minute = int(params[1])
        return time(hour, minute)
    except (ValueError, IndexError):
        return None


def ToKeyboard(lst: list, previous_data: str) -> list:    
    buttons = []
    for element in lst:
        buttons.append(InlineKeyboardButton(str(element[0]), callback_data=f"{previous_data}/{element[1]}"))
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(*buttons)
    cancel = InlineKeyboardButton("Cancel", callback_data="CANCEL")
    keyboard.add(cancel)
    
    return keyboard


def PageArrows(page: int) -> InlineKeyboardMarkup:
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️", callback_data=f"-{page}"))
    if page < 2:
        buttons.append(InlineKeyboardButton("➡️", callback_data=f"+{page}"))
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(*buttons)
    
    return keyboard

def ToPollParams(params: list) -> list:
    poll_parameters = []
    
    string = ""
    quiz = False
    multichoice = False
    anonymous = False
    
    for param in params:
        if param[0] != "-":
            string = f"{string} {param}"
        elif param[1] == "o":
            poll_parameters.append(string)
            string = ""
        elif param[1] == "c":
            poll_parameters.append(string)
            correct = len(poll_parameters) - 1
            string = ""
            quiz = True
        elif param[1] == "m":
            multichoice = True
        elif param[1] == "a":
            anonymous = True
    poll_parameters.append(string)
        
    return poll_parameters, quiz, multichoice, correct, anonymous