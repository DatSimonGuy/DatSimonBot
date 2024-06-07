from ..types.databases.tagDatabase import TagDatabase
from .databaseModule import DatabaseModule
import telebot.async_telebot as async_telebot
from telebot.types import Message
import random

class TagModule(DatabaseModule):
    def __init__(self, bot, elements_type: str):
        super().__init__(bot)
        self._database: TagDatabase = TagDatabase(f"data/{elements_type}")
        self._load()

    async def add_tag(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            atributes = self._parse_input(message, "tag")

            if "tag" not in atributes:
                raise ValueError("You need to specify a tag.")
            
            self._database.add_tag(message.chat.id, atributes["tag"])
            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def remove_tag(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            atributes = self._parse_input(message, "tag")

            if "tag" not in atributes:
                raise ValueError("You need to specify a tag.")
            
            self._database.remove_tag(message.chat.id, atributes["tag"])
            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    def random_element(self, message: Message) -> str:
        atributes = self._parse_input(message, "tag")
        
        if "tag" not in atributes:
            raise ValueError("You need to specify a tag.")
        
        elements = self._database.get_elements(message.chat.id, atributes["tag"])
        
        if len(elements) == 0:
            raise ValueError("No elements found.")
        
        return random.choice(elements)