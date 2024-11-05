""" Module for handling text messages """

from telegram import Update
from telegram.ext import filters, ContextTypes
import telegram.ext
from dsb.types.module import BaseModule, prevent_edited, admin_only

class MessageHandler(BaseModule):
    """ Module for handling text messages """
    def __init__(self, ptb, telebot) -> None:
        super().__init__(ptb, telebot)
        self._handlers = {
            "who_am_i": self._user_info,
            "whoami": self._user_info,
            "what_broke": self._what_broke,
        }
        self._descriptions = {
            "who_am_i": "Get user id",
            "whoami": "Get user id (alias)",
            "what_broke": "Get the last 10 messages in the chat",
        }
        self._messages = {}
        self._message_handler = telegram.ext.MessageHandler(filters.ALL & ~filters.COMMAND,
                              self._handle_text)

    def add_handlers(self) -> None:
        """ Add handlers """
        super().add_handlers()
        self._bot.add_handler(self._message_handler)

    def remove_handlers(self) -> None:
        """ Remove handlers """
        super().remove_handlers()
        self._bot.remove_handler(self._message_handler)

    @property
    def messages(self) -> dict:
        """ Returns the list of messages """
        return self._messages

    @admin_only
    @prevent_edited
    async def _what_broke(self, update: Update, _) -> None:
        """ Get last log message """
        if not self._dsb.logs:
            await update.message.reply_text("No logs available")
            return
        message = self._dsb.logs[-1]
        await update.message.reply_text(f"```{message}```", parse_mode="Markdownv2")

    @prevent_edited
    async def _user_info(self, update: Update, _) -> None:
        """ Get user info """
        id_info = f"```user_id:\n{update.message.from_user.id}\n```"
        await update.message.reply_text(f"{id_info}", parse_mode="Markdownv2")

    @prevent_edited
    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Handle text messages """
        if "🫰" in update.message.text:
            user = update.message.from_user
            is_admin = await context.bot.get_chat_member(update.message.chat_id,
                                                   user.id).status in ["creator", "administrator"]
            if not user.id in self._dsb.config.get("admins", []) and not is_admin:
                return
            if update.message.reply_to_message:
                await context.bot.delete_message(chat_id=update.message.chat_id,
                                                  message_id=update.message.message_id)
                return
        if update.message.chat_id not in self._messages:
            self._messages[update.message.chat_id] = [update.message]
        else:
            self._messages[update.message.chat_id].append(update.message)
        for messages in self._messages.values():
            if len(messages) > 10:
                messages.pop(0)
