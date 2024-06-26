from .databaseModule import DatabaseModule
from telebot.async_telebot import AsyncTeleBot
from ...types.databases.keyDatabase import KeyDatabase
from telebot.types import Message
from .adminTools import AdminTools
from dotenv import load_dotenv
import os

class MainHandlerModule(DatabaseModule):
    used = True
    
    def __init__(self, bot: AsyncTeleBot, *args, **kwargs) -> None:
        super().__init__(bot)

        self._commands = {
            "aaaa": self
        }

        self._database: KeyDatabase = KeyDatabase("data/people")
        self._database.load()

        self._create_admin()

        bot.register_message_handler(content_types=["text"], callback=self._register_message, regexp=r"^(?!\/)(?!http).*", pass_bot=True)
    
    def _new_person(self, id: int, name: str, admin: bool, group_id: int):
        self._database.setArg(id, "admin", admin)
        self._database.setArg(id, "groups", set([group_id]))
        self._database.setArg(id, "name", name)
        self._database.setArg(id, "sent_messages", {group_id: 0})

    def _create_admin(self):
        load_dotenv()
        owner_id = int(os.getenv("DEV_ID"))

        if self._database.exists(owner_id):
            return

        owner_name = os.getenv("DEV_NAME")
        self._new_person(owner_id, owner_name, True, owner_id)
    
    def _create_person(self, message: Message):
        person_username = message.from_user.username
        person_id = message.from_user.id
        self._new_person(person_id, person_username, False, message.chat.id)
    
    async def _register_message(self, message: Message, bot: AsyncTeleBot):
        person_id = message.from_user.id

        if self._database.exists(person_id):
            groups = set(self._database.getArg(person_id, "groups"))

            if message.chat.id not in groups:
                groups.add(message.chat.id)
                self._database.setArg(person_id, "groups", groups)

            sent_messages = self._database.getArg(person_id, "sent_messages")

            current_value = sent_messages.get(message.chat.id, None)

            if current_value is None:
                sent_messages[message.chat.id] = 1
            else:
                sent_messages[message.chat.id] += 1

            self._database.setArg(person_id, "sent_messages", sent_messages)
            return
        
        self._create_person(message)