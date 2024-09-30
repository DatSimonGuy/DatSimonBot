""" Youtube module for telebot """

import io
from typing import Generator, Literal
import scrapetube
import pytubefix as pytube
from pytubefix.exceptions import VideoUnavailable
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from .base.base_module import BaseModule, prevent_edited

def search(query: str, limit: int | None = None, # pylint: disable=too-many-arguments, too-many-positional-arguments
           sleep: int = 1, sort_by: Literal['relevance',
           'upload_date', 'view_count', 'rating'] = "relevance",
           results_type: Literal['video', 'channel', 'playlist',
           'movie'] = "video") -> Generator[dict, None, None]:
    """ Search for videos on youtube """
    return scrapetube.get_search(query, limit, sleep, sort_by, results_type)


def get_video(url: str) -> pytube.Stream:
    """ Get the highest resolution stream of a youtube video """
    try:
        video = pytube.YouTube(url)
        return video.streams.get_highest_resolution()
    except VideoUnavailable:
        return None

class YtModule(BaseModule):
    """ Youtube module for telebot """
    def __init__(self, bot, telebot_module) -> None:
        super().__init__(bot, telebot_module)
        self._handlers = {
            "download": self._download,
            "ytsearch": self._ytsearch
        }
        self._descriptions = {
            "download": "Download a youtube video",
            "ytsearch": "Search for a youtube video"
        }
        self._auto_download_groups = set()

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

        video = get_video(" ".join(args))

        if video is None:
            await message.reply_text("The video is not available")
            return

        if video.filesize_mb > 50:
            await message.reply_text("The video is too large to send")
            return

        video_data = io.BytesIO()

        video.stream_to_buffer(video_data)

        video_data.seek(0)

        video_file = InputFile(video_data, filename=f"{video.title}.mp4")

        await update.message.reply_video(video_file)

    @prevent_edited
    async def _ytsearch(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            results = search(" ".join(context.args), limit=1)
        for result in results:
            await update.message.reply_text(f"https://youtu.be/{result['videoId']}")
