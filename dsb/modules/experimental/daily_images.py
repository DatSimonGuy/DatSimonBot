""" Fun stuff to play with """

import os
import random
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
        sets = self._dsb.database.get_table("sets")
        chat_id = update.effective_chat.id
        set_name = " ".join(args)
        if sets.get_row(check_function=lambda x: x[1] == chat_id and x[2] == set_name):
            await update.message.reply_text("Set already exists")
            return
        sets.add_row([chat_id, set_name, f"images/{chat_id}/{set_name}"])
        sets.save()
        await update.message.reply_text("Set created")

    async def _delete_set(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Delete a set for daily images """
        args, _ = self._get_args(context)
        if not args:
            await update.message.reply_text("Please provide a set name")
            return
        sets = self._dsb.database.get_table("sets")
        chat_id = update.effective_chat.id
        sets.remove_row(check_function=lambda x: x[1] == chat_id and x[2] == " ".join(args))
        sets.save()
        await update.message.reply_text("Set deleted")

    async def _daily_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Toggle daily image for given set """
        args, kwargs = self._get_args(context)
        if "set" not in kwargs:
            image_set = " ".join(args)
        else:
            image_set = kwargs["set"]
        chat_id = update.effective_chat.id
        if not image_set:
            sets = self._dsb.database.get_table("sets")
            chat_sets = sets.get_rows(check_function=lambda x: x[1] == chat_id)
            chat_sets = [x[1] for x in chat_sets]
            await update.message.reply_text("Avaible sets:\n" + "\n".join(chat_sets))
            return
        image_toggles = self._dsb.database.get_table("image_toggles")
        current_toggle = image_toggles\
            .get_row(check_function=lambda x: x[1] == chat_id and x[2] == image_set)
        if current_toggle:
            current_toggle[2] = image_set
            image_toggles.replace_row(current_toggle[0], current_toggle)
        else:
            image_toggles.add_row([chat_id, image_set])
        image_toggles.save()
        await update.message.reply_text("I will now send images from this set daily at 6 am")

    async def _cancel_daily_image(self, update: Update, _) -> None:
        """ Cancel daily image """
        chat_id = update.effective_chat.id
        image_toggles = self._dsb.database.get_table("image_toggles")
        image_toggles.remove_row(check_function=lambda x: x[1] == chat_id)
        image_toggles.save()
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
        sets = self._dsb.database.get_table("sets")
        chat_id = update.effective_chat.id
        set_to_update = sets\
            .get_rows(check_function=lambda x: x[1] == chat_id and x[2] == image_set)
        if not set_to_update:
            await update.message.reply_text("Set not found")
            return
        self._dsb.database.save_file(image_bytes, set_to_update[3])
        await update.message.reply_text("Image submitted to set")

    def _get_image(self, image_set: str, chat_id: int) -> bytes:
        """ Get Arthur quote image """
        sets = self._dsb.database.get_table("sets")
        images_path = sets.\
            get_row(check_function=lambda x: x[1] == chat_id and x[2] == image_set)[3]
        images = self._dsb.database.list_all(images_path)
        random_img = random.choice(images)
        image = self._dsb.database.load_file(os.path.join(images_path, random_img))
        return image

    async def _send_daily_image(self) -> None:
        """ Send daily image quote """
        image_toggles = self._dsb.database.get_table("image_toggles")
        for chat_id, image_set in image_toggles.get_rows():
            image = self._get_image(image_set, chat_id)
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
            chat_id = update.effective_chat.id
            sets = self._dsb.database.get_table("sets")
            chat_sets = sets.get_rows(check_function=lambda x: x[1] == chat_id)
            chat_sets = [x[1] for x in chat_sets]
            await update.message.reply_text("Avaible sets:\n" + "\n".join(chat_sets))
            return
        image = self._get_image(image_set, update.effective_chat.id)
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
        self._dsb.database.add_table("image_toggles", [("chat_id", int), ("image_set", str)])
        self._dsb.database.add_table("sets", [("chat_id", int),
                                              ("image_set", str), ("image_dir", str)])
        return super().prepare()
