""" Fun stuff to play with """

import random
from telegram import Update
from telegram.ext import ContextTypes
from dsb.types.module import BaseModule

class DailyImages(BaseModule):
    """ Misc module for DSB. """
    def __init__(self, bot, dsb):
        super().__init__(bot, dsb)
        self._image_sets = {}
        self._image_dir = "daily_images"
        self._daily_job = None
        self._handlers = {
            "create_set": self._create_set,
            "delete_set": self._delete_set,
            "daily_image": self._daily_image,
            "cancel_daily_image": self._cancel_daily_image,
            "submit_image": self._submit_image,
            "random_image": self._random_image,
        }
        self._descriptions = {
            "create_set": "Create a new set for daily images",
            "delete_set": "Delete a set for daily images",
            "daily_image": "Toggle daily image for given set",
            "cancel_daily_image": "Cancel daily image",
            "submit_image": "Submit an image to a set",
            "random_image": "Send a random image from a set",
        }

    async def _create_set(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Create a new set for daily images """
        args, _ = self._get_args(context)
        if not args:
            await update.message.reply_text("Please provide a set name")
            return
        self._dsb.database.create_dir(f"{update.effective_chat.id}/{self._image_dir}/{args}")
        await update.message.reply_text("Set created")

    async def _delete_set(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Delete a set for daily images """
        args, _ = self._get_args(context)
        if not args:
            await update.message.reply_text("Please provide a set name")
            return
        self._dsb.database.delete_dir(f"{update.effective_chat.id}/{self._image_dir}/{args}")
        await update.message.reply_text("Set deleted")

    async def _daily_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Toggle daily image for given set """
        args, kwargs = self._get_args(context)
        if "set" not in kwargs:
            image_set = " ".join(args)
        else:
            image_set = kwargs["set"]
        if not image_set:
            await update.message.reply_text("Avaible sets:\n" + \
                "\n".join(self._dsb.database.list_all("daily_images")))
            return
        self._image_sets[update.message.chat_id] = image_set
        await update.message.reply_text("I will now send images from this set daily at 6 am")

    async def _cancel_daily_image(self, update: Update, _) -> None:
        """ Cancel daily image """
        self._image_sets.pop(update.message.chat_id, None)
        await update.message.reply_text("Daily image cancelled")

    async def _submit_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Submit an Arthur quote """
        args, kwargs = self._get_args(context)
        if "set" not in kwargs:
            image_set = " ".join(args)
        else:
            image_set = kwargs["set"]
        if not update.message.photo:
            if not update.message.reply_to_message:
                await update.message.reply_text("Reply to a message with the image")
                return
            quote = update.message.reply_to_message
        else:
            quote = update.message
        file = await quote.photo[-1].get_file()
        if not file:
            await update.message.reply_text("No file found")
            return
        image_bytes = await file.download_as_bytearray()
        self._dsb.database.save_image(image_bytes,
                                      f"{update.effective_chat.id}/{self._image_dir}/{image_set}",
                                      f"{quote.message_id}")
        await update.message.reply_text("Image submitted to set")

    def _get_image(self, image_set: str, chat_id: int) -> bytes:
        """ Get Arthur quote image """
        images = self._dsb.database.list_all(f"{chat_id}/{self._image_dir}/{image_set}")
        random_img = random.choice(images)
        random_img = random_img.split(".")[0]
        image = self._dsb.database.load_image(f"{chat_id}/{self._image_dir}/{image_set}",
                                              random_img)
        return image

    async def _send_daily_image(self) -> None:
        """ Send Arthur quote """
        for chat_id, image_set in self._image_sets.items():
            image = self._get_image(image_set, chat_id)
            if not image:
                break
            await self._bot.bot.send_photo(chat_id, image)

    async def _random_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Send a random Arthur quote """
        args, kwargs = self._get_args(context)
        if "set" not in kwargs:
            image_set = " ".join(args)
        else:
            image_set = kwargs["set"]
        if not image_set:
            await update.message.reply_text("Avaible sets:\n" + \
                "\n".join(self._dsb.database.list_all("daily_images")))
            return
        image = self._get_image(image_set, update.message.chat_id)
        await update.message.reply_photo(image)

    def add_handlers(self):
        """ Add handlers """
        self._daily_job = self._dsb.scheduler.every().day.at("06:00").do(self._send_daily_image)
        return super().add_handlers()

    def remove_handlers(self):
        """ Remove handlers """
        self._dsb.scheduler.cancel_job(self._daily_job)
        return super().remove_handlers()

    def prepare(self):
        """ Prepare the module """
        self._image_sets = self._dsb.database.load('misc', 'arthur_toggles')
        return super().prepare()
