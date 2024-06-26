from ...types.databases.tagDatabase import TagDatabase
from .databaseModule import DatabaseModule
import telebot.async_telebot as async_telebot
from telebot.types import Message
import random

class TagModule(DatabaseModule):
    used = False
    
    def __init__(self, bot: async_telebot.AsyncTeleBot, dir_name: str):
        super().__init__(bot)
        self._database: TagDatabase = TagDatabase(f"data/{dir_name}")
        self._load()

    async def _add_tag(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            atributes = self._parse_input(message, "tag")

            if "tag" not in atributes:
                raise ValueError("You need to specify a tag.")
            
            self._database.add_tag(message.chat.id, atributes["tag"])
            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def _remove_tag(self, message: Message, bot: async_telebot.AsyncTeleBot):
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
        """ Get a random element from the database at the specified tag

        Args:
            message (Message): message containing the tag

        Raises:
            ValueError: when no tag is specified
            ValueError: when no elements are found

        Returns:
            str: random element

        """
        atributes = self._parse_input(message, "tag")
        
        if "tag" not in atributes:
            raise ValueError("You need to specify a tag.")
        
        elements = self._database.get_elements(message.chat.id, atributes["tag"])
        
        if len(elements) == 0:
            raise ValueError("No elements found.")
        
        return random.choice(elements)