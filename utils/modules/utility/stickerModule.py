from ...types.databases.tagDatabase import TagDatabase
from .tagModule import TagModule
import telebot.async_telebot as async_telebot
from telebot.types import Message

class StickerModule(TagModule):
    used = True
    
    def __init__(self, bot):
        super().__init__(bot, "stickers")
        self._commands = {
            "add_sticker_tag": self._add_tag,
            "remove_sticker_tag": self._remove_tag,
            "add_sticker": self._add_sticker,
            "remove_sticker": self._remove_sticker,
            "sticker": self._sticker
        }
    
    async def _add_sticker(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            atributes = self._parse_input(message, "tag")

            if "tag" not in atributes:
                raise ValueError("You need to specify a tag.")
            
            if atributes["tag"] not in self._database.get_tags(message.chat.id):
                self._database.add_tag(message.chat.id, atributes["tag"])
            
            if atributes.get("sticker_id", None) is None:
                raise ValueError("You need to reply to a sticker.")
            
            self._database.add_element(message.chat.id, atributes["tag"], atributes["sticker_id"])
            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def _remove_sticker(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            atributes = self._parse_input(message, "tag")

            if "tag" not in atributes or "idx" not in atributes:
                raise ValueError("You need to specify a tag and an index.")
            
            self._database.remove_element(message.chat.id, atributes["tag"], atributes["idx"])
            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return

    async def _sticker(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            sticker = self.random_element(message)
            if message.reply_to_message:
                await bot.send_sticker(message.chat.id, reply_to_message_id=message.reply_to_message.id, sticker=sticker)
            else:
                await bot.send_sticker(message.chat.id, sticker)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return