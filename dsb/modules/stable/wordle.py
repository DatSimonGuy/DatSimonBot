""" Wordle module """

import datetime
import requests
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
            "wordleAmongUs": "Get all words required to get amongus image in wordle"
        }
        self._words = self.load_file("wordle_words.txt").decode().split("\n")
        self._answer = ""

    async def _get_correct_letters(self, word: str, letter: str | None = None) -> int:
        """ Get the number of correct letters in the word """
        if letter:
            return sum(1 for i in range(5) if word[i] == self._answer[i] and word[i] == letter)
        return sum(1 for i in range(5) if word[i] == self._answer[i])

    async def _get_color(self, word: str, letter: int) -> int:
        """ Get color of the letter """
        if word[letter] == self._answer[letter]:
            return 1
        if word[letter] in self._answer and \
                word[:letter].count(word[letter]) + \
                    await self._get_correct_letters(word, word[letter]) \
                < self._answer.count(word[letter]):
            return 2
        return 0

    async def _get_words_for_image(self, image: list[list[int]]) -> list[str] | str:
        """ Get the first word that matches each row of the image """
        words = []
        for row in image:
            valid_words = self._words
            for i in range(5):
                valid_words = [word for word in valid_words
                               if await self._get_color(word, i) == row[i]]
            if valid_words:
                words.append(valid_words[0])
            else:
                words = "Impossible"
                return words
        return words

    async def _create_visual_representation(self, image: list[list[int]]) -> str:
        """ Create visual representation of the image """
        representation = ""
        for row in image:
            for pixel in row:
                representation += ["⬛", "🟩", "🟨", ][pixel]
            representation += "\n"
        return representation

    async def _get_amogus(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Get all words required to get amongus image in wordle """ 
        url = f"https://www.nytimes.com/svc/wordle/v2/{datetime.date.today():%Y-%m-%d}.json"
        self._answer = requests.get(url, timeout=10).json()["solution"]

        args, _ = self._get_args(context)
        if args and len(args[0]) != 5:
            await update.message.reply_text("To słowo nie ma 5 liter")
            return
        if args:
            self._answer = args[0]

        base_images = {
            "green_yellow": [
                [0, 1, 1, 1, 0],
                [0, 2, 2, 1, 1],
                [0, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
                [0, 1, 0, 1, 0]
            ],
            "yellow_green": [
                [0, 2, 2, 2, 0],
                [0, 1, 1, 2, 2],
                [0, 2, 2, 2, 2],
                [0, 2, 2, 2, 0],
                [0, 2, 0, 2, 0]
            ],
            "black_yellow": [
                [1, 0, 0, 0, 1],
                [1, 2, 2, 0, 0],
                [1, 0, 0, 0, 0],
                [1, 0, 0, 0, 1],
                [1, 0, 1, 0, 1]
            ],
            "yellow_black": [
                [1, 2, 2, 2, 1],
                [1, 0, 0, 2, 2],
                [1, 2, 2, 2, 2],
                [1, 2, 2, 2, 1],
                [1, 2, 1, 2, 1]
            ],
            "black_green": [
                [2, 0, 0, 0, 2],
                [2, 1, 1, 0, 0],
                [2, 0, 0, 0, 0],
                [2, 0, 0, 0, 2],
                [2, 0, 2, 0, 2]
            ],
            "green_black": [
                [2, 1, 1, 1, 2],
                [2, 0, 0, 1, 1],
                [2, 1, 1, 1, 1],
                [2, 1, 1, 1, 2],
                [2, 1, 2, 1, 2]
            ]
        }

        def reverse_image(image):
            return [row[::-1] for row in image]

        def alternate_image(image):
            bg = image[0][0]
            new_image = [row[1:] for row in image]
            for row in new_image:
                row.append(bg)
            return new_image

        images_dict = {
            key: {
                "original": image,
                "reversed": reverse_image(image),
                "alternate": alternate_image(image),
                "reversed_alternate": reverse_image(alternate_image(image))
            }
            for key, image in base_images.items()
        }

        reply_message = ""

        for name, image in images_dict.items():
            reply_message += f"{name}:\n"
            for key, variant in image.items():
                words = await self._get_words_for_image(variant)
                if words == "Impossible":
                    reply_message += f"{key}: Impossible\n"
                else:
                    reply_message += \
                        f"{key}: \n{await self._create_visual_representation(variant)}\n"
                    reply_message += f"{', '.join(words)}\n"
            reply_message += "\n"

        await update.message.reply_text(reply_message)
