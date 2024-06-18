from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from .databaseModule import DatabaseModule
from ...types.databases.keyDatabase import KeyDatabase
import os
import jsonpickle
import matplotlib.pyplot as plt
import schedule
import uuid

class StatisticsModule(DatabaseModule):
    used = True
    
    def __init__(self, bot: AsyncTeleBot) -> None:
        super().__init__(bot)

        self._commands = {
            "activity": self._daily_activity,
            "top": self._top_senders,
            "bottom": self._bottom_senders
        }

        self._database: KeyDatabase = KeyDatabase("data/people", read_only=True)

        self._last_group_activity: KeyDatabase = KeyDatabase("data/activity")
        self._last_group_activity.load()

        if not self._last_group_activity.exists(0):
            self._last_group_activity.setArg(0, "done_today", False)

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

    def _top_list(self, message):
        self._database.load()

        senders = self._database.find(lambda key, val: key != "groups" or (key == "groups" and message.chat.id in val))

        scores = []

        for sender in senders:
            sent_messages = self._database.getArg(sender, "sent_messages")
            name = self._database.getArg(sender, "name")
            scores.append((name, sent_messages[message.chat.id]))
        
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores

    async def _top_senders(self, message: Message, bot: AsyncTeleBot):
        try:
            args = self._parse_input(message, "ammount")
        except ValueError:
            args = {}
        
        scores = self._top_list(message)

        try:
            ammount = int(args.get("ammount", len(scores)))
        except ValueError:
            await bot.reply_to(message, "You passed invalid number as the argument")
            return

        top_message = "Top senders in this chat:\n"

        top_message += '\n'.join(f"{score[0]}: {score[1]}" for score in scores[:ammount])

        await bot.send_message(message.chat.id, top_message)
    
    async def _bottom_senders(self, message: Message, bot: AsyncTeleBot):
        try:
            args = self._parse_input(message, "ammount")
        except ValueError:
            args = {}
        
        scores = self._top_list(message)

        try:
            ammount = int(args.get("ammount", len(scores)))
        except ValueError:
            await bot.reply_to(message, "You passed invalid number as the argument")
            return
        
        scores.reverse()

        bottom_message = "Bottom senders in this chat:\n"

        bottom_message += '\n'.join(f"{score[0]}: {score[1]}" for score in scores[:ammount])

        await bot.send_message(message.chat.id, bottom_message)

    async def _daily_activity(self, message: Message, bot: AsyncTeleBot):
        if not self._last_group_activity.getArg(0, "done_today"):
            self._log_daily_activity()
            self._last_group_activity.setArg(0, "done_today", True)

        try:
            args = self._parse_input(message, "type")
        except ValueError:
            args = {}

        names = []
        names_2 = []
        today_activity = []
        total_activity = []

        group_id = message.chat.id

        if args.get("type", None) == "all":
            scores = self._top_list(message)
            for score in scores:
                names_2.append(score[0])
                total_activity.append(score[1])

        max_file_num = -1

        for file in os.listdir("data/activity/group_logs"):
            file_num = int(file.replace("group_activity_log", "").replace(".json", ""))
            if file_num > max_file_num:
                max_file_num = file_num

        if max_file_num == -1:
            await bot.reply_to(message, "No logs yet")
            return

        with open(f"data/activity/individual_logs/individual_activity_log{max_file_num}.json", "r") as f:
            group_daily_individual_activity = jsonpickle.decode(f.read(), keys=True)

        activity = []
        today_activity = list(group_daily_individual_activity[group_id].values())

        self._database.load()

        for i, person in enumerate(group_daily_individual_activity[group_id]):
            activity.append((self._database.getArg(person, "name"), today_activity[i]))
        
        activity.sort(key=lambda x: x[1], reverse=True)

        for i, a in enumerate(activity):
            names.append(a[0])
            today_activity[i] = a[1]

        try:
            ammount = int(args.get("num", max(len(total_activity), len(today_activity))))
        except ValueError:
            await bot.reply_to(message, "You passed invalid number as the argument")
            return

        hard_limit = int(os.getenv("PEOPLE_LIMIT")) # This is for visibility purposes
        
        ammount = min(ammount, hard_limit)

        if total_activity:
            plt.bar(names_2[:ammount], total_activity[:ammount], color="green")
            plt.bar(names[:ammount], today_activity[:ammount], color="blue")
            plt.legend(["Total activity", "Today's activity"])
        else:
            plt.bar(names[:ammount], today_activity[:ammount], color="blue")
            plt.legend(["Today's activity"])

        plt.ylabel("Number of messages")
        if max(today_activity) > 0:
            plt.yscale("log")
        plt.title("Activity for group")

        unique_id = uuid.uuid4()
        plt.savefig(f"data/activity/plot{unique_id}.png")

        with open(f"data/activity/plot{unique_id}.png", 'rb') as f:
            await bot.send_photo(message.chat.id, f)
        
        plt.close()
        
        os.remove(f"data/activity/plot{unique_id}.png")