""" Fun stuff to play with """

import random
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from dsb.types.module import BaseModule

class DailyImages(BaseModule):
    """ Misc module for DSB. """
    def __init__(self, bot, dsb):
        super().__init__(bot, dsb)
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
        sets = context.chat_data.get("sets", None)
        if sets is None:
            context.chat_data["sets"] = set()
            sets = context.chat_data["sets"]
        elif not isinstance(sets, set):
            sets = set()
            sets = context.chat_data["sets"]
        set_name = " ".join(args)
        if set_name in sets:
            await update.message.reply_text("Set already exists")
            return
        context.chat_data["sets"].add(set_name)
        await update.message.reply_text("Set created")

    async def _delete_set(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Delete a set for daily images """
        args, _ = self._get_args(context)
        sets: set = context.chat_data.get("sets", None)
        if sets is None:
            await update.message.reply_text("No sets to delete")
            return
        if not args:
            await update.message.reply_text("Please provide a set name")
            return
        sets.remove(" ".join(args))
        await update.message.reply_text("Set deleted")

    async def _daily_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Toggle daily image for given set """
        args, kwargs = self._get_args(context)
        if "set" not in kwargs:
            image_set = " ".join(args)
        else:
            image_set = kwargs["set"]
        if not image_set:
            sets: set = context.chat_data.get("sets", None)
            await update.message.reply_text("Avaible sets:\n" + "\n".join(sets))
            return
        context.bot_data["daily_images"].update({update.effective_chat.id: image_set})
        await update.message.reply_text("I will now send images from this set daily at 6 am")

    async def _cancel_daily_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Cancel daily image """
        context.bot_data["daily_images"].pop(update.effective_chat.id, None)
        await update.message.reply_text("Daily image cancelled")

    async def _submit_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Submit an Arthur quote """
        sets: set = context.chat_data.get("sets", None)
        if sets is None:
            await update.message.reply_text("No sets to submit to")
            return
        args, kwargs = self._get_args(context)
        if "set" not in kwargs:
            image_set = " ".join(args)
        else:
            image_set = kwargs["set"]
        if not update.message.photo:
            if not update.message.reply_to_message:
                await update.message.reply_text("Reply to a message with the image")
                return
            msg = update.message.reply_to_message
        else:
            msg = update.message
        file = await msg.photo[-1].get_file()
        if not file:
            await update.message.reply_text("No file found")
            return
        image_bytes = await file.download_as_bytearray()
        if image_set not in sets:
            await update.message.reply_text("Set not found")
            return
        self._dsb.database.save_image(update.effective_chat.id,
                                      f"{image_set}/file.file_id", image_bytes)
        await update.message.reply_text("Image submitted to set")

    def _get_image(self, chat_id: int, set_name: str) -> bytes:
        """ Get Arthur quote image """
        images = self._dsb.database.list_files(f"{chat_id}/{set_name}")
        if not images:
            return None
        image_name = random.choice(images)
        image = self._dsb.database.get_image(chat_id, image_name)
        return image

    async def _send_daily_image(self) -> None:
        """ Send daily image quote """
        for chat_id, set_name in self._bot.bot_data["daily_images"].items():
            image = self._get_image(chat_id, set_name)
            if not image:
                continue
            await self._bot.bot.send_photo(chat_id, image)

    async def _random_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Send a random image from a set """
        args, kwargs = self._get_args(context)
        if "set" not in kwargs:
            image_set = " ".join(args)
        else:
            image_set = kwargs["set"]
        if not image_set:
            sets = context.chat_data.get("sets", None)
            sets = list(sets.keys())
            await update.message.reply_text("Avaible sets:\n" + "\n".join(sets))
            return
        image = self._get_image(update.effective_chat.id, image_set)
        if not image:
            await update.message.reply_text("No images found / no set with this name")
            return
        await update.message.reply_photo(image)

    def add_handlers(self):
        """ Add handlers """
        loop = asyncio.get_event_loop()
        self._daily_job = self._dsb.scheduler.every().\
            day.at("06:00").do(lambda: loop.create_task(self._send_daily_image()))
        return super().add_handlers()

    def remove_handlers(self):
        """ Remove handlers """
        self._dsb.scheduler.cancel_job(self._daily_job)
        return super().remove_handlers()

    def prepare(self):
        """ Prepare the module """
        self._dsb.set_value("daily_images", {})
        return super().prepare()
