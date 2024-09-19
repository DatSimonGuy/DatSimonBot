""" Youtube module for telebot """

import io
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from dsb_main.modules.stable.youtube import Youtube
from .base.base_module import BaseModule, prevent_edited

class YtModule(BaseModule):
    """ Youtube module for telebot """
    def __init__(self, bot, telebot_module) -> None:
        super().__init__(bot, telebot_module)
        self._handlers = {
            "download": self._download,
            "ytsearch": self.ytsearch,
            "allow_auto_download": self._allow_auto_download,
            "disallow_auto_download": self._disallow_auto_download
        }
        self._descriptions = {
            "download": "Download a youtube video",
            "ytsearch": "Search for a youtube video",
            "allow_auto_download": "Allow auto downloading in a group",
            "disallow_auto_download": "Disallow auto downloading in a group"
        }
        self._auto_download_groups = set()
        self._youtube = None
        self._db = None
        self.add_handlers()

    @prevent_edited
    async def _download(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """  Send a youtube video """
        if update.message.reply_to_message:
            message = update.message.reply_to_message
            args = context.args or [update.message.reply_to_message.text]
        else:
            message = update.message
            args = context.args

        if not args:
            await message.reply_text("Please provide a youtube link")
            return

        video = self._youtube.get_video(" ".join(args))

        if video.filesize_mb > 50:
            await message.reply_text("The video is too large to send")
            return

        video_data = io.BytesIO()

        video.stream_to_buffer(video_data)

        video_data.seek(0)

        video_file = InputFile(video_data, filename=f"{video.title}.mp4")

        await update.message.reply_video(video_file)

    @prevent_edited
    async def ytsearch(self, update, context) -> None:
        """ Search for a youtube video """
        if not context.args:
            await update.message.reply_text("Please provide a search query")
            return
        args, kwargs = self._get_args(context)
        if "limit" in kwargs:
            try:
                results = self._youtube.search(" ".join(args), limit=int(kwargs["limit"]))
            except ValueError:
                await update.message.reply_text("Invalid limit")
        else:
            results = self._youtube.search(" ".join(context.args), limit=1)
        for result in results:
            await update.message.reply_text(f"https://youtu.be/{result['videoId']}")

    @prevent_edited
    async def _allow_auto_download(self, update: Update, _) -> None:
        """ Allow auto downloading in a group """
        group_id = update.message.chat.id
        if group_id not in self._auto_download_groups:
            self._auto_download_groups.add(group_id)
            self._db.save(self._auto_download_groups, f"{group_id}/yt_module",
                          "auto_download_groups")
        await update.message.set_reaction("✅")

    @prevent_edited
    async def _disallow_auto_download(self, update: Update, _) -> None:
        """ Disallow auto downloading in a group """
        group_id = update.message.chat.id
        if group_id in self._auto_download_groups:
            self._auto_download_groups.remove(group_id)
            self._db.save(self._auto_download_groups, f"{group_id}/yt_module",
                          "auto_download_groups")
        await update.message.set_reaction("✅")

    def prepare(self) -> bool:
        """ Prepare the module """
        self._youtube: Youtube = self._telebot_module.get_dsb_module("Youtube")
        self._db = self._telebot_module.get_dsb_module("Database")
        self._auto_download_groups = self._db.load("yt_module", "auto_download_groups",
                                                   default=set())
        if not self._youtube:
            self._telebot_module.log("ERROR", "Youtube module not found")
            return False
        if not self._db:
            self._telebot_module.log("ERROR", "Database module not found")
            return False
        return True
