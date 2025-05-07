""" Backup module"""

import os
import shutil
from telegram import Update
from telegram.ext import Application, ContextTypes
from dsb.old_dsb import DSB
from dsb.types.module import BaseModule, HandlerType

class Backup(BaseModule):
    """ Backup module """
    def __init__(self, bot: Application, telebot_module: DSB) -> None:
        super().__init__(bot, telebot_module)
        self._handlers = {
            "backup": (self._backup, HandlerType.BOT_ADMIN),
            "restore": (self._restore, HandlerType.BOT_ADMIN)
        }
        self._descriptions = {
            "backup": "Send a backup of the database",
            "restore": "Restore the database from a backup"
        }

    async def _backup(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Create backup of the database and send it to the user. (Admin only)
        
        Usage: /backup [--no-images]

        Command parameters
        -----------
        no-images: (Optional) 
            Don't include images in the backup.
        """
        database_path = self._dsb.config["database_path"]
        _, kwargs = self._get_args(context)
        if "no-images" in kwargs:
            _ = shutil.copytree(database_path, "temp",
                                ignore=lambda _, y: [name for name in y
                                                     if name.endswith(".jpg")
                                                     or name.endswith(".png")])
            shutil.make_archive("backup", "zip", "temp")
            shutil.rmtree("temp")
        else:
            shutil.make_archive("backup", "zip", database_path)
        try:
            with open("backup.zip", "rb") as file:
                await update.message.reply_document(file.read(), filename="backup.zip")
        except FileNotFoundError:
            await update.message.reply_text("Failed to create backup")
        finally:
            os.remove("backup.zip")

    async def _restore(self, update: Update, _) -> None:
        """
        Restore the database from a backup file. (Admin only)
        
        Usage: /restore (reply to backup file)
        """
        reply = update.message.reply_to_message
        if not reply or not reply.document or not reply.document.file_name.endswith(".zip"):
            await update.message.reply_text("Please reply to a valid backup file")
            return
        backup = await update.message.reply_to_message.document.get_file()
        save_path = await backup.download_to_drive()
        database_path = self._dsb.config["database_path"]
        shutil.unpack_archive(save_path, database_path)
        os.remove(save_path)
        await self._dsb.reload_data()
        await update.message.reply_text("Database restored")
