from .tagModule import TagModule
import telebot.async_telebot as async_telebot
from telebot.types import Message

class GifModule(TagModule):
    used = True
    
    def __init__(self, bot):
        super().__init__(bot, "gifs")
        self._commands = {
            "add_gif_tag": self._add_tag,
            "remove_gif_tag": self._remove_tag,
            "add_gif": self._add_gif,
            "remove_gif": self._remove_gif,
            "gif": self._gif
        }
    
    async def _add_gif(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            atributes = self._parse_input(message, "tag")

            if "tag" not in atributes:
                raise ValueError("You need to specify a tag.")
            
            if atributes["tag"] not in self._database.get_tags(message.chat.id):
                self._database.add_tag(message.chat.id, atributes["tag"])
            
            if atributes.get("document_id", None) is None:
                raise ValueError("You need to reply to a gif.")
            
            self._database.add_element(message.chat.id, atributes["tag"], atributes["document_id"])
            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return
    
    async def _remove_gif(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            atributes = self._parse_input(message, "tag")

            if "tag" not in atributes or "idx" not in atributes:
                raise ValueError("You need to specify a tag and an index.")
            
            self._database.remove_element(message.chat.id, atributes["tag"], atributes["idx"])
            await self._confirm(message, bot)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return

    async def _gif(self, message: Message, bot: async_telebot.AsyncTeleBot):
        try:
            gif = self.random_element(message)
            if message.reply_to_message:
                await bot.send_document(message.chat.id, gif, reply_to_message_id=message.reply_to_message.message_id)
            else:
                await bot.send_document(message.chat.id, gif)
        except ValueError as e:
            await bot.send_message(message.chat.id, str(e))
            return