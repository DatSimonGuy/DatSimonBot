from telebot.async_telebot import AsyncTeleBot
from ..dsbModule import DsbModule
from telebot.types import Message
import scrapetube
from dotenv import load_dotenv
import os
import random
from pytube import YouTube
import schedule

load_dotenv()

class YoutubeModule(DsbModule):
    def __init__(self, bot: AsyncTeleBot) -> None:
        commands = {
            "mission": self._todays_mission
        }
        super().__init__(bot, commands)
        schedule.every().day.at("00:00").do(self._remove_mission)
        self._last_mission = None

    def _remove_mission(self) -> None:
        if os.path.exists("data/todays_mission/mission.mp4"):
            os.remove("data/todays_mission/mission.mp4")

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

        await bot.send_video(message.chat.id, open("data/todays_mission/mission.mp4", "rb"))

        
        