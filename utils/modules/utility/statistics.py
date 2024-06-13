from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from .databaseModule import DatabaseModule
from ...types.databases.keyDatabase import KeyDatabase
import os
import jsonpickle
import matplotlib.pyplot as plt
import schedule

class Statistics(DatabaseModule):
    def __init__(self, bot: AsyncTeleBot, database: KeyDatabase) -> None:
        commands = {
            "activity": self._daily_activity
        }
        super().__init__(bot, commands)
        self._database: KeyDatabase = database
        self._last_group_activity: KeyDatabase = KeyDatabase("data/activity")
        self._last_group_activity.setArg(0, "done_today", False)
        self._last_group_activity.load()
        self._last_individual_activity: KeyDatabase = KeyDatabase("data/activity", 1)
        self._last_individual_activity.load()
        schedule.every().day.at("00:00").do(self._next_day)
    
    def _next_day(self):
        self._last_group_activity.setArg(0, "done_today", False)
    
    def _log_daily_activity(self):
        people = self._database.get_all_entries()

        group_daily_activity = {}
        group_daily_individual_activity = {}

        for person in people:
            sent_messages = self._database.getArg(person, "sent_messages")

            for group in sent_messages:

                if group not in group_daily_activity:
                    group_daily_activity[group] = 0

                group_daily_activity[group] += sent_messages[group]

                if group not in group_daily_individual_activity:
                    group_daily_individual_activity[group] = {}

                previous_person_activity = self._last_individual_activity.getArg(person, "sent_messages")

                if previous_person_activity is None:
                    previous_person_activity = {}

                group_daily_individual_activity[group][person] = sent_messages[group] - previous_person_activity.get(group, 0)

            self._last_individual_activity.setArg(person, "sent_messages", sent_messages)
            
        for group in group_daily_activity:
            last_activity = self._last_group_activity.getArg(group, "activity")
            group_daily_activity[group] -= last_activity if last_activity else 0
            self._last_group_activity.setArg(group, "activity", last_activity if last_activity else 0 + group_daily_activity[group])

        os.makedirs("data/activity/group_logs", exist_ok=True)
        os.makedirs("data/activity/individual_logs", exist_ok=True)

        max = -1
        for file in os.listdir("data/activity/group_logs"):
            file_num = int(file.replace("group_activity_log", "").replace(".json", ""))
            if file_num > max:
                max = file_num

        with open(f"data/activity/group_logs/group_activity_log{max + 1}.json", "w") as f:
            f.write(jsonpickle.encode(group_daily_activity, keys=True))
        
        with open(f"data/activity/individual_logs/individual_activity_log{max + 1}.json", "w") as f:
            f.write(jsonpickle.encode(group_daily_individual_activity, keys=True))

    async def _daily_activity(self, message: Message, bot: AsyncTeleBot):
        if not self._last_group_activity.getArg(0, "done_today"):
            self._log_daily_activity()
            self._last_group_activity.setArg(0, "done_today", True)

        group_id = message.chat.id

        max = -1
        for file in os.listdir("data/activity/group_logs"):
            file_num = int(file.replace("group_activity_log", "").replace(".json", ""))
            if file_num > max:
                max = file_num

        if max == -1:
            await bot.reply_to(message, "No logs yet")
            return

        with open(f"data/activity/individual_logs/individual_activity_log{max}.json", "r") as f:
            group_daily_individual_activity = jsonpickle.decode(f.read(), keys=True)

        names = []
        for person in group_daily_individual_activity[group_id]:
            names.append(self._database.getArg(person, "name"))

        today_activity = list(group_daily_individual_activity[group_id].values())

        plt.bar(names, today_activity)
        plt.savefig(f"data/activity/plot{group_id}.png")

        with open(f"data/activity/plot{group_id}.png", 'rb') as f:
            await bot.send_photo(message.chat.id, f)
        
        os.remove(f"data/activity/plot{group_id}.png")