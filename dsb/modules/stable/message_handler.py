""" Module for handling text messages """

import asyncio
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
            "unsilly": self._unsilly
        }
        self._descriptions = {
            "who_am_i": "Get user id",
            "whoami": "Get user id (alias)",
            "what_broke": "Get last log message",
        }
        self._handled_emotes = {
            "🫰": self._snap,
            "📊": self._ynpoll,
            "➕": self._repeat
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
    async def _unsilly(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Decode from silly language """
        args, _ = self._get_args(context)
        qwerty = "qwertyuiopasdfg hjklzxcvbnm"
        symbols1 = '1234567890@#$_&-+()/*"' + "'" + ':;!?'
        symbols2 = r'~`|•√π÷×§∆£¢€¥^°={}\%©®™✓[]'
        if not update.message.reply_to_message:
            return
        if not update.message.reply_to_message.text:
            return
        text = update.message.reply_to_message.text
        for char in text:
            if char not in qwerty:
                continue
            if args and args[0] == "2":
                char = symbols2[qwerty.index(char)]
            else:
                char = symbols1[qwerty.index(char)]
        for i, char in enumerate(symbols1):
            text = text.replace(char, qwerty[i])
        for i, char in enumerate(symbols2):
            text = text.replace(char, qwerty[i])
        await update.message.reply_text(text)

    async def _snap(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Send a message """
        user = update.message.from_user
        user_data = await context.bot.get_chat_member(update.message.chat_id, user.id)
        is_admin = user_data.status in ["creator", "administrator"]
        if not str(user.id) in self._dsb.config.get("admins", []) and not is_admin:
            return
        if update.message.reply_to_message:
            await asyncio.sleep(1)
            to_delete = update.message.reply_to_message.message_id
            await context.bot.delete_message(chat_id=update.message.chat_id,
                                                message_id=to_delete)
            return

    async def _ynpoll(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Send a yes/no poll """
        if not update.message.reply_to_message:
            return
        question = update.message.reply_to_message.text
        await context.bot.send_poll(update.message.chat_id, question,
                                           ["Yes", "No"], is_anonymous=False)

    async def _repeat(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Repeat a message """
        if not update.message.reply_to_message:
            return
        if not update.message.reply_to_message.text:
            return
        await context.bot.send_message(update.message.chat_id,
                                        update.message.reply_to_message.text)

    async def _nerd_detection(self, update: Update, _) -> None:
        """ Detect nerds """
        await update.message.set_reaction("🤓")

    @prevent_edited
    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Handle text messages """
        if update.message.text in self._handled_emotes:
            await self._handled_emotes[update.message.text](update, context)
            return
        if update.message.text and len(update.message.text) > 200:
            await self._nerd_detection(update, context)
            return
        if update.message.chat_id not in self._messages:
            self._messages[update.message.chat_id] = [update.message]
        else:
            self._messages[update.message.chat_id].append(update.message)
        for messages in self._messages.values():
            if len(messages) > 10:
                messages.pop(0)
