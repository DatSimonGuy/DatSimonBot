from telegram import Update
from telegram.ext import ContextTypes
from dsb.types.module import BaseModule

class Wordle(BaseModule):
    """ Module for functions related to wordle """
    def __init__(self, bot, dsb):
        super().__init__(bot, dsb)
        self._handlers = {
            "wordleAmongUs": self._get_amogus
        }
        self._descriptions = {
            "wordle": "Get all words required to get amongus image in wordle"
        }
        self._words = 

    async def _get_correct_letters(self, word: str, letter: str | None = None) -> int:
        """ Get the number of correct letters in the word """
        if letter:
            return sum([1 for i in range(5) if word[i] == WORDLE_ANSWER[i] and word[i] == letter])
        return sum([1 for i in range(5) if word[i] == WORDLE_ANSWER[i]])

    async def _get_color(word: str, letter: int) -> int:
        """ Get color of the letter """
        if word[letter] == WORDLE_ANSWER[letter]:
            return 1
        elif word[letter] in WORDLE_ANSWER and \
                word[:letter].count(word[letter]) + self._get_correct_letters(word, word[letter]) \
                < WORDLE_ANSWER.count(word[letter]):
            return 2
        return 0

    async def _get_row(self, colors: list) -> list[str]:
        """ Get all words that match the color row """
        valid_words = words
        for i in range(5):
            valid_words = [word for word in valid_words if get_color(word, i) == colors[i]]

        return valid_words

    async def _get_amogus(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Get all words required to get amongus image in wordle """
        