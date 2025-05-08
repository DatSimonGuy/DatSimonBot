""" Module for handling text messages """

import os
import asyncio
import random
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import filters, ContextTypes
import telegram.ext
import pronouncing
from pydub import AudioSegment
import speech_recognition as sr
from dsb.types.module import BaseModule, HandlerType

class MessageHandler(BaseModule):
    """ Module for handling text messages """
    def __init__(self, ptb, telebot) -> None:
        super().__init__(ptb, telebot)
        self._handlers = {
            "who_am_i": (self._user_info, HandlerType.DEFAULT),
            "who_are_you": (self._sender_info, HandlerType.DEFAULT),
            "whoami": (self._user_info, HandlerType.DEFAULT),
            "what_broke": (self._what_broke, HandlerType.BOT_ADMIN),
            "stt": (self._stt, HandlerType.DEFAULT),
            "silly_cipher": (self._silly_cipher, HandlerType.DEFAULT),
            "random_haiku": (self._get_random_haiku, HandlerType.DEFAULT),
            "silly": (self._make_silly, HandlerType.INLINE),
            "cls": (self._clear_chat, HandlerType.INLINE),
            "clear": (self._clear_chat, HandlerType.INLINE),
            "f": (self._format_text, HandlerType.INLINE),
            "format": (self._format_text, HandlerType.INLINE)
        }
        self._descriptions = {
            "who_am_i": "Get user id",
            "whoami": "Get user id (alias)",
            "what_broke": "Get last log message",
            "silly_cipher": "Decode or encode from silly language",
            "stt": "Transcribe voice message",
            "random_haiku": "Get a random haiku from the chat"
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

    async def _what_broke(self, update: Update, _) -> None:
        """
        Get last log message. (Admin only)
        
        Usage: /what_broke
        """
        if not self._dsb.logs:
            await update.message.reply_text("No logs available")
            return
        message = self._dsb.logs[-1]
        await update.message.reply_text(f"```{message}```", parse_mode="Markdownv2")

    async def _user_info(self, update: Update, _) -> None:
        """
        Get user info.
        
        Usage: /who_am_i
        """
        id_info = f"Your id: `{update.message.from_user.id}`"
        await update.message.reply_text(f"{id_info}", parse_mode="Markdownv2")

    async def _sender_info(self, update: Update, _) -> None:
        """
        Get sender info.
        
        Usage: /who_are_you (reply to message)
        """
        if update.message.reply_to_message:
            id_info = f"Their id: `{update.message.reply_to_message.from_user.id}`"
            await update.message.reply_text(f"{id_info}", parse_mode="Markdownv2")
        else:
            await update.message.reply_text("Reply to a message to get the sender id")

    def cipher(self, text: str) -> str:
        """ Encode or decode text to silly language """
        big_qwerty = "QWERTYUIOPASDFG HJKLZXCVBNM"
        qwerty = "qwertyuiopasdfg hjklzxcvbnm"
        symbols1 = '1234567890@#$_&-+()/*"' + "'" + ':;!?'
        symbols2 = r'~`|•√π÷×§∆£¢€¥^°={}\%©®™✓[]'
        text = list(text)
        for i, char in enumerate(text):
            if char in qwerty:
                text[i] = symbols1[qwerty.index(char)]
            elif char in big_qwerty:
                text[i] = symbols2[big_qwerty.index(char)]
            elif char in symbols1:
                text[i] = qwerty[symbols1.index(char)]
            elif char in symbols2:
                text[i] = big_qwerty[symbols2.index(char)]
        text = "".join(text)
        return text

    async def _clear_chat(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """ Clear chat messages """
        message = "." + "\n" * 100 + "."
        result = [InlineQueryResultArticle(id="1", title="Clear the chat screen",
                                           description="Long ahh message",
                                           input_message_content=InputTextMessageContent(message))]
        await update.inline_query.answer(result)

    async def _format_text(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """ Format message in different ways """
        query = update.inline_query.query
        query = " ".join(query.split()[1:])
        if not query:
            return
        doubled = f"{query}\n\n{query}"
        fire = "🔥".join(query)
        random_cap = "".join([char.upper() if random.random() > 0.5 else char for char in query])
        result = [
            InlineQueryResultArticle(id="1", title="Geen_Geen",
                                     description="Double the input",
                                     input_message_content=InputTextMessageContent(doubled)),
            InlineQueryResultArticle(id="2", title="Fire",
                                     description="Add fire emojis",
                                     input_message_content=InputTextMessageContent(fire)),
            InlineQueryResultArticle(id="3", title="Random capitalization",
                                     description="Randomly capitalize",
                                     input_message_content=InputTextMessageContent(random_cap))]
        await update.inline_query.answer(result)

    async def _make_silly(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """ Make silly text """
        query = update.inline_query.query
        query = " ".join(query.split()[1:])
        if not query:
            return
        text = self.cipher(query)
        result = [InlineQueryResultArticle(id="1", title="Silly text",
                                           description=text,
                                           input_message_content=InputTextMessageContent(text))]
        await update.inline_query.answer(result)

    async def _silly_cipher(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Encode or decode text to silly language.
        
        Usage: /silly_cipher (reply to message)
        """
        if not update.message.reply_to_message:
            return
        if not update.message.reply_to_message.text:
            return
        text = self.cipher(update.message.reply_to_message.text)
        await update.message.reply_text(text)

    async def _snap(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Remove a message """
        user = update.message.from_user
        user_data = await context.bot.get_chat_member(update.message.chat_id, user.id)
        is_admin = user_data.status in ["creator", "administrator"]
        if not user.id in self._dsb.admins and not is_admin:
            return
        if update.message.reply_to_message:
            await asyncio.sleep(1)
            to_delete = update.message.reply_to_message.message_id
            await context.bot.delete_message(chat_id=update.message.chat_id,
                                                message_id=to_delete)
            return

    async def _ynpoll(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Send a yes/no poll. """
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

    async def _stt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Send a transcription of the voice message.
        
        Usage: /stt [--language <language>] (reply to voice message)
        
        Command parameters
        -----------
        language : text (optional)
            The language to use for transcription. Default is Polish.
            For example: pl-PL, en-US, de-DE, etc.
        """
        if not update.message.reply_to_message:
            return
        if not update.message.reply_to_message.voice:
            return

        await update.message.reply_text("Transcribing...")

        args, _ = self._get_args(context)

        if args:
            language=args[0]
        else:
            language="pl-PL"

        # Download the voice file
        file = await update.message.reply_to_message.voice.get_file()
        os.makedirs("dsb/database/temp", exist_ok=True)
        oga_path = f"dsb/database/temp/{os.path.basename(file.file_path)}"
        flac_path = oga_path.replace(".oga", ".flac")
        await file.download_to_drive(oga_path)

        try:
            sound = AudioSegment.from_file(oga_path, format="ogg")
            sound.export(flac_path, format="flac")
            r = sr.Recognizer()
            with sr.AudioFile(flac_path) as source:
                audio = r.record(source)
            text = r.recognize_google(audio, language=language)
            await update.message.reply_text(f"Transcription: {text}")
        except sr.UnknownValueError:
            await update.message.reply_text("Could not understand the audio.")
        except sr.RequestError:
            await update.message.reply_text("Error fetching response.")
        except Exception as e: # pylint: disable=W0718
            await update.message.reply_text(f"An error occurred: {e}")
        finally:
            # Clean up temporary files
            if os.path.exists(oga_path):
                os.remove(oga_path)
            if os.path.exists(flac_path):
                os.remove(flac_path)

    def __detect_haikus(self, message: str) -> str | None:
        """ Detect haikus in a message """
        words = message.split()
        def count_syllables(word: str):
            if word in r".,:;'\/?()+=-_[]{}*&^%$#@!~`":
                return 0
            phones = pronouncing.phones_for_word(word.lower())
            if not phones:
                return 1
            return pronouncing.syllable_count(phones[0])
        syllables = [count_syllables(word) for word in words]
        lines = [[], [], []]
        lines_length = [5, 7, 5]
        current_line = 0
        for i, s in enumerate(syllables):
            if lines_length[current_line] - s > 0:
                lines[current_line].append(words[i])
                lines_length[current_line] -= s
            elif lines_length[current_line] - s == 0:
                lines[current_line].append(words[i])
                current_line += 1
                if current_line > 2 and i != len(words) - 1:
                    return None
                elif current_line > 2:
                    return "\n".join(" ".join(line) for line in lines)
            else:
                return None
        return None

    async def _get_random_haiku(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Sends a random haiku from the current chat
        
        Usage: /random_haiku
        
        """
        haikus: dict = context.chat_data.get("haikus", None)
        if haikus is None:
            await update.message.reply_text("No one has made any haikus yet")
            return
        random_user = random.choice(list(haikus.keys()))
        random_haiku = random.choice(haikus[random_user])
        await update.message.reply_text(random_haiku)

    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """ Handle text messages """
        if update.message.text and update.message.text in self._handled_emotes:
            await self._handled_emotes[update.message.text](update, context)
            return
        if update.message.text is not None:
            detected_haikus = self.__detect_haikus(update.message.text)
            if detected_haikus is not None:
                haiku_message = await update.message.reply_text(detected_haikus +
                                                f"\n\n- {update.effective_user.username}")
                haikus: dict = context.chat_data.get("haikus", None)
                user = update.effective_user.username
                if haikus is not None:
                    user_haikus = haikus.get(user, None)
                    if user_haikus is None:
                        haikus[user] = [haiku_message.text]
                    else:
                        user_haikus.append(haiku_message.text)
                else:
                    context.chat_data["haikus"] = {user: [haiku_message.text]}
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
