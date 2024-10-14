""" Fun stuff to play with """

import random
from telegram import Update
from dsb.types.module import BaseModule

class MiscModule(BaseModule):
    """ Misc module for DSB. """
    def __init__(self, bot, dsb):
        super().__init__(bot, dsb)
        self._arthur_toggles = {}
        self._quote_dir = "quotes"
        self._arthur_job = None
        self._handlers = {
            "daily_arthur": self._daily_arthur,
            "submit_arthur": self._submit_arthur,
            "random_arthur": self._random_arthur_quote,
        }
        self._descriptions = {
            "daily_arthur": "Daily Arthur toggle",
            "submit_arthur": "Submit an Arthur quote",
        }

    async def _daily_arthur(self, update: Update, _) -> None:
        """ Toggle daily Arthur """
        self._arthur_toggles[update.message.chat_id] = \
            not self._arthur_toggles.get(update.message.chat_id, False)
        await update.message.reply_text("Daily Arthur is now " + \
            f"{'on' if self._arthur_toggles[update.message.chat_id] else 'off'}")

    async def _submit_arthur(self, update: Update, _) -> None:
        """ Submit an Arthur quote """
        if not update.message.photo:
            if not update.message.reply_to_message:
                await update.message.reply_text("Reply to a message with the quote")
                return
            quote = update.message.reply_to_message
        else:
            quote = update.message
        file = await quote.photo[-1].get_file()
        if not file:
            await update.message.reply_text("No file found")
            return
        image_bytes = await file.download_as_bytearray()
        self._dsb.database.save_image(image_bytes, self._quote_dir, f"{quote.message_id}")
        await update.message.reply_text("Quote submitted")

    def _get_arthur_quote(self) -> bytes:
        """ Get Arthur quote image """
        quotes = self._dsb.database.list_all(self._quote_dir)
        random_quote = random.choice(quotes)
        random_quote = random_quote.split(".")[0]
        quote = self._dsb.database.load_image(self._quote_dir, random_quote)
        return quote

    async def _send_arthur_quote(self) -> None:
        """ Send Arthur quote """
        for chat_id, toggle in self._arthur_toggles.items():
            if toggle:
                quote = self._get_arthur_quote()
                if not quote:
                    break
                await self._bot.bot.send_photo(chat_id, quote)

    async def _random_arthur_quote(self, update: Update, _) -> None:
        """ Send a random Arthur quote """
        quote = self._get_arthur_quote()
        if not quote:
            await update.message.reply_text("No quotes found")
            return
        await update.message.reply_photo(quote)

    def add_handlers(self):
        """ Add handlers """
        self._arthur_job = self._dsb.scheduler.every().day.at("06:00").do(self._send_arthur_quote)
        return super().add_handlers()

    def remove_handlers(self):
        """ Remove handlers """
        self._dsb.scheduler.cancel_job(self._arthur_job)
        return super().remove_handlers()

    def prepare(self):
        """ Prepare the module """
        self._arthur_toggles = self._dsb.database.load('misc', 'arthur_toggles')
        return super().prepare()
