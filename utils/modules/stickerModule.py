from ..types.databases.tagDatabase import TagDatabase
from .dsbModule import DsbModule
import telebot.async_telebot as async_telebot
from telebot.types import Message
import random

class StickerModule(DsbModule):
    def __init__(self, bot):
        super().__init__(bot)
        self._database = TagDatabase("data/stickers")
        self._load()
    
    def _add_handlers(self, bot):
        bot.register_message_handler(self.add_tag, commands=["add_tag"], pass_bot=True)
        bot.register_message_handler(self.remove_tag, commands=["remove_tag"], pass_bot=True)
        bot.register_message_handler(self.add_sticker, commands=["add_sticker"], pass_bot=True)
        bot.register_message_handler(self.remove_sticker, commands=["remove_sticker"], pass_bot=True)
        bot.register_message_handler(self.sticker, commands=["sticker"], pass_bot=True)
    
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
    
    async def add_sticker(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            atributes = self._parse_input(message, "tag")

            if "tag" not in atributes:
                raise ValueError("You need to specify a tag.")
            
            if atributes["tag"] not in self._database.get_tags(message.chat.id):
                self._database.add_tag(message.chat.id, atributes["tag"])
            
            if atributes["sticker_id"] is None:
                raise ValueError("You need to reply to a sticker.")
            
            self._database.add_element(message.chat.id, atributes["tag"], atributes["sticker_id"])
            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def remove_sticker(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            atributes = self._parse_input(message, "tag")

            if "tag" not in atributes or "idx" not in atributes:
                raise ValueError("You need to specify a tag and an index.")
            
            self._database.remove_element(message.chat.id, atributes["tag"], atributes["idx"])
            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return

    async def sticker(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            atributes = self._parse_input(message, "tag")

            if "tag" not in atributes:
                raise ValueError("You need to specify a tag.")
            
            stickers = self._database.get_elements(message.chat.id, atributes["tag"])

            if len(stickers) == 0:
                raise ValueError("No stickers found.")
            
            sticker = random.choice(stickers)
            if message.reply_to_message:
                await bot.send_sticker(message.chat.id, reply_to_message_id=message.reply_to_message.id, sticker=sticker)
            else:
                await bot.send_sticker(message.chat.id, sticker)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return