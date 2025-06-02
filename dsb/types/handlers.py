from telegram.ext import CommandHandler, CallbackQueryHandler, \
    InvalidCallbackData, ContextTypes
from telegram.ext.filters import User, BaseFilter, UpdateType
from telegram import Update
from dsb.utils.button_picker import CallbackData

class DSBCommandHandler(CommandHandler):
    def __init__(self, command, callback, filters = None, block = ..., has_args = None):
        if isinstance(filters, BaseFilter):
            filters = filters & ~UpdateType.EDITED_MESSAGE
        else:
            filters = ~UpdateType.EDITED_MESSAGE
        super().__init__(command, callback, filters, block, has_args)

class AdminCommandHandler(DSBCommandHandler):
    def __init__(self, dsb, command, callback, filters = None, block = ..., has_args = None):
        for admin in dsb.admins:
            if isinstance(filters, BaseFilter):
                filters = filters & User(admin)
            else:
                filters = User(admin)
        super().__init__(command, callback, filters, block, has_args)

class CallbackHandler(CallbackQueryHandler):
    async def handle_update(self, update: Update, application,
                            check_result, context: ContextTypes.DEFAULT_TYPE):
        if isinstance(update.callback_query.data, InvalidCallbackData):
            await update.effective_message.delete()
            await update.callback_query.answer(text="This request was too old", show_alert=True)
            return
        callback : CallbackData = update.callback_query.data[1]
        if update.effective_user.id != callback.caller:
            return
        if callback.data.get("cancel", False):
            await context.bot.delete_message(chat_id=update.effective_chat.id,
                                       message_id=update.effective_message.id)
            return
        return super().handle_update(update, application, check_result, context)