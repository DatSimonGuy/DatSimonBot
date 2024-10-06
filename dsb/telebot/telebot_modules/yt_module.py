""" Youtube module for telebot """

import os
from typing import Generator, Literal
from typing import Optional
import scrapetube
import yt_dlp
from telegram import Update
from telegram.ext import ContextTypes
from .base.base_module import BaseModule, prevent_edited

def search(query: str, limit: int | None = None, # pylint: disable=too-many-arguments, too-many-positional-arguments
           sleep: int = 1, sort_by: Literal['relevance',
           'upload_date', 'view_count', 'rating'] = "relevance",
           results_type: Literal['video', 'channel', 'playlist',
           'movie'] = "video") -> Generator[dict, None, None]:
    """ Search for videos on youtube """
    return scrapetube.get_search(query, limit, sleep, sort_by, results_type)

def get_video_info(url: str) -> Optional[dict]:
    """ Get video info """
    try:
        ydl_opts = {
            'quiet': True,
        }
        video = yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
        return video
    except Exception: # pylint: disable=broad-except
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

        sent_message = await message.reply_text("Getting video info...")
        video = get_video_info(" ".join(args))

        if video is None:
            await message.reply_text("The video is not available")
            return

        if video["duration"] > 600:
            await message.reply_text("The video is too large to send")
            return

        dl_ops = {
            'outtmpl': 'dsb/temp/%(id)s.%(ext)s',
            'quiet': True,
            'format': 'best[ext=mp4]/best',
        }

        os.makedirs("dsb/temp", exist_ok=True)
        video_path = f"dsb/temp/{video['id']}.mp4"
        try:
            await sent_message.edit_text("Downloading the video...")
            yt_dlp.YoutubeDL(dl_ops).download([video["webpage_url"]])
            with open(video_path, "rb") as video_file:
                video = video_file.read()
            try:
                await sent_message.delete()
            except Exception: # pylint: disable=broad-except
                pass
            await update.message.reply_video(video, write_timeout=60, read_timeout=60)
        except Exception: # pylint: disable=broad-except
            await message.reply_text("Failed to download the video")
            return
        finally:
            os.remove(video_path)

    @prevent_edited
    async def _ytsearch(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Search for a youtube video """
        if not context.args:
            await update.message.reply_text("Please provide a search query")
            return
        args, kwargs = self._get_args(context)
        if "limit" in kwargs:
            try:
                results = search(" ".join(args), limit=int(kwargs["limit"]))
            except ValueError:
                await update.message.reply_text("Invalid limit")
        else:
            results = search(" ".join(context.args), limit=1)
        for result in results:
            await update.message.reply_text(f"https://youtu.be/{result['videoId']}")
