""" Fun stuff to play with """

import os
import random
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from dsb.types.module import BaseModule

def save_file(file: bytes, path: str) -> None:
    """ Save a file """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as file_:
        file_.write(file)

def load_file(path: str) -> bytes:
    """ Load a file """
    try:
        with open(path, "rb") as file:
            return file.read()
    except FileNotFoundError:
        return b""

def list_all(path: str) -> list[str]:
    """ List all files in a directory """
    try:
        return os.listdir(path)
    except FileNotFoundError:
        return []

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
            context.chat_data["sets"] = {}
            sets = context.chat_data["sets"]
        chat_id = update.effective_chat.id
        set_name = " ".join(args)
        if sets.get(set_name, None):
            await update.message.reply_text("Set already exists")
            return
        database_path = self._dsb.config["database_path"]
        context.chat_data["sets"][set_name] = f"{database_path}/{chat_id}/images/{set_name}"
        await update.message.reply_text("Set created")

    async def _delete_set(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Delete a set for daily images """
        args, _ = self._get_args(context)
        if not args:
            await update.message.reply_text("Please provide a set name")
            return
        sets = context.chat_data.get("sets", None)
        if not sets:
            await update.message.reply_text("No sets found")
            return
        sets.pop(" ".join(args), None)
        await update.message.reply_text("Set deleted")

    async def _daily_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Toggle daily image for given set """
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
        context.bot_data["daily_images"].update({update.effective_chat.id: image_set})
        await update.message.reply_text("I will now send images from this set daily at 6 am")

    async def _cancel_daily_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Cancel daily image """
        context.bot_data["daily_images"].pop(update.effective_chat.id, None)
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
            msg = update.message.reply_to_message
        else:
            msg = update.message
        file = await msg.photo[-1].get_file()
        if not file:
            await update.message.reply_text("No file found")
            return
        image_bytes = await file.download_as_bytearray()
        sets = context.chat_data.get("sets", None)
        set_to_update = sets.get(image_set, None)
        if not set_to_update:
            await update.message.reply_text("Set not found")
            return
        database_path = self._dsb.config["database_path"]
        save_file(image_bytes, database_path + set_to_update[3] + f"/{file.file_id}.png")
        await update.message.reply_text("Image submitted to set")

    def _get_image(self, path: str) -> bytes:
        """ Get Arthur quote image """
        if not path:
            return b""
        images = list_all(path)
        if not images:
            return b""
        random_img = random.choice(images)
        image = load_file(os.path.join(path, random_img))
        return image

    async def _send_daily_image(self) -> None:
        """ Send daily image quote """
        for chat_id, image_path in self._bot.bot_data["daily_images"].items():
            image = self._get_image(image_path)
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
        image = self._get_image(context.chat_data["sets"][image_set])
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
