""" Youtube module for commands related to youtube """

from typing import Literal, Generator
import pytubefix as pytube
import scrapetube
from dsb_main.modules.base_modules.module import Module, run_only

class Youtube(Module):
    """ Youtube module """
    name = "Youtube"

    @run_only
    def search(self, query: str, limit: int | None = None,
               sleep: int = 1, sort_by: Literal['relevance',
               'upload_date', 'view_count', 'rating'] = "relevance",
               results_type: Literal['video', 'channel', 'playlist',
               'movie'] = "video") -> Generator[dict, None, None]:
        """ Search for videos on youtube """
        return scrapetube.get_search(query, limit, sleep, sort_by, results_type)

    @run_only
    def get_video(self, url: str) -> pytube.Stream:
        """ Get the highest resolution stream of a youtube video """
        video = pytube.YouTube(url)
        return video.streams.get_highest_resolution()
