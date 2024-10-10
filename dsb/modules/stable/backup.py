""" Backup module"""

from telegram import Update
from telegram.ext import Application
from dsb.dsb import DSB
from dsb.types.module import BaseModule, prevent_edited, admin_only

class Backup(BaseModule):
    """ Backup module """
    def __init__(self, bot: Application, telebot_module: DSB) -> None:
        super().__init__(bot, telebot_module)
        self._handlers = {
            "backup": self._backup
        }
        self._descriptions = {
            "backup": "Send a backup of the database"
        }

    @admin_only
    @prevent_edited
    async def _backup(self, update: Update, _) -> None:
        database = self._dsb.database
        if database is None:
            await update.message.reply_text("No database found")
            return
        await update.message.reply_document(database.backup(), filename="backup.zip")
