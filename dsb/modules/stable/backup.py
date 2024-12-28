""" Backup module"""

import os
import shutil
from telegram import Update
from telegram.ext import Application
from dsb.engine import DSBEngine
from dsb.types.module import BaseModule, prevent_edited, admin_only

class Backup(BaseModule):
    """ Backup module """
    def __init__(self, bot: Application, telebot_module: DSBEngine) -> None:
        super().__init__(bot, telebot_module)
        self._handlers = {
            "backup": self._backup,
            "restore": self._restore
        }
        self._descriptions = {
            "backup": "Send a backup of the database",
            "restore": "Restore the database from a backup"
        }

    @admin_only
    @prevent_edited
    async def _backup(self, update: Update, _) -> None:
        database_path = self._dsb.config["database_path"]
        shutil.make_archive("backup", "zip", database_path)
        try:
            with open("backup.zip", "rb") as file:
                await update.message.reply_document(file.read(), filename="backup.zip")
        except FileNotFoundError:
            await update.message.reply_text("Failed to create backup")
        finally:
            os.remove("backup.zip")

    @admin_only
    @prevent_edited
    async def _restore(self, update: Update, _) -> None:
        reply = update.message.reply_to_message
        if not reply or not reply.document or not reply.document.file_name.endswith(".zip"):
            await update.message.reply_text("Please reply to a valid backup file")
            return
        backup = await update.message.reply_to_message.document.get_file()
        await backup.download_to_drive("./backup.zip")
        database_path = self._dsb.config["database_path"]
        shutil.unpack_archive("backup.zip", database_path)
        os.remove("backup.zip")
        await self._dsb.reload_data()
        await update.message.reply_text("Database restored")
