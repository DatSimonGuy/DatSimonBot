from telebot.async_telebot import AsyncTeleBot
from .databaseModule import DatabaseModule
from telebot.types import Message
import scrapetube
from dotenv import load_dotenv
import os
import random
from pytube import YouTube
import schedule
from ...types.databases.keyDatabase import KeyDatabase

load_dotenv()

class YoutubeModule(DatabaseModule):
    used = True
    
    def __init__(self, bot: AsyncTeleBot, *args, **kwargs) -> None:
        super().__init__(bot)

        self._commands = {
            "mission": self._todays_mission,
            "auto_download": self._allow_auto_download,
            "no_auto_download": self._disallow_auto_download
        }

        bot.register_message_handler(callback=self._auto_download, content_types=["text"], regexp=r"https?://(?:www\.)?youtu(?:\.be|be\.com)/\S+", pass_bot=True)

        schedule.every().day.at("00:00").do(self._remove_mission)

        data_saving = bool(kwargs.get("data_saving", False))

        self._last_mission = None
        self._database: KeyDatabase = KeyDatabase("data/youtube/auto_download")
        self._database.load()
        self._data_saving = data_saving

    def _remove_mission(self) -> None:
        if os.path.exists("data/todays_mission/mission.mp4"):
            os.remove("data/todays_mission/mission.mp4")
    
    async def _allow_auto_download(self, message: Message, bot: AsyncTeleBot) -> None:
        self._database.setArg(message.chat.id, "auto_download", True)
        await bot.send_message(message.chat.id, "Auto download enabled.")
    
    async def _disallow_auto_download(self, message: Message, bot: AsyncTeleBot) -> None:
        self._database.setArg(message.chat.id, "auto_download", False)
        await bot.send_message(message.chat.id, "Auto download disabled.")
    
    async def _auto_download(self, message: Message, bot: AsyncTeleBot) -> None:
        if self._data_saving:
            await bot.send_message(message.chat.id, "Data saving is enabled by the developer. Can't download videos.")
            return
        
        if self._database.getArg(message.chat.id, "auto_download"):
            os.makedirs("data/youtube/videos", exist_ok=True)
            video_url = message.text
            
            video = YouTube(video_url)

            if video.length > int(os.getenv("MAX_VIDEO_LENGTH")):
                await bot.send_message(message.chat.id, f"Can't download videos longer than {os.getenv('MAX_VIDEO_LENGTH')} seconds.")
                return
            
            video.streams.filter(progressive=True, file_extension='mp4').first().download(output_path="data/youtube/videos/", filename="video.mp4")
            await bot.send_video(message.chat.id, open("data/youtube/videos/video.mp4", "rb"))
            os.remove("data/youtube/videos/video.mp4")
            if message.chat.type != "private" and (await bot.get_me()).id in (await bot.get_chat_administrators(message.chat.id)):
                await bot.delete_message(message.chat.id, message.id)

    async def _todays_mission(self, message: Message, bot: AsyncTeleBot) -> None:
        if not os.path.exists("data/todays_mission/mission.mp4"):

            os.makedirs("data/todays_mission", exist_ok=True)

            chanel_id = os.getenv('MISSION_CHANNEL_ID')
            videos = scrapetube.get_channel(chanel_id, content_type="shorts")
            found_videos = []
            
            for video in videos:
                if "TODAY'S MISSION:" in video["headline"]["simpleText"] and video["videoId"] != self._last_mission:
                    found_videos.append(video)
                else:
                    break

            if len(found_videos) == 0:
                await bot.send_message(message.chat.id, "No mission found.")
                return

            random_video = random.choice(found_videos)
            self._last_mission = random_video["videoId"]
            video_url = "https://www.youtube.com/watch?v="+str(random_video['videoId'])
            YouTube(video_url).streams.filter(progressive=True, file_extension='mp4').first().download(output_path="data/todays_mission/", filename="mission.mp4")

        await bot.send_video(message.chat.id, open("data/todays_mission/mission.mp4", "rb"), caption="Auto downloaded video")

        
        