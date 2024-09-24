""" Miscelanious module for telebot. """

from telegram import Update
from dsb_main.modules.stable.miscelanious import Miscelanious
from .base.base_module import BaseModule, admin_only, prevent_edited

class Misc(BaseModule):
    """ Miscelanious module """
    def __init__(self, bot, telebot_module) -> None:
        super().__init__(bot, telebot_module)
        self._miscelanious_module: Miscelanious = None
        self._handlers = {
            "is_stos_alive": self._is_stos_alive,
            "screenshot": self._screenshot
        }
        self._descriptions = {
            "is_stos_alive": "Check if stos is alive (Admin only)",
            "screenshot": "Take a screenshot of a page"
        }

    @admin_only
    @prevent_edited
    async def _is_stos_alive(self, update: Update, _) -> None:
        """ Check if stos is alive """
        await update.message.reply_text("Checking if stos is alive..." + \
                                        "(Might take up to 30 minutes)")
        elapsed_time = await self._miscelanious_module.is_stos_alive()
        if elapsed_time == -1:
            await update.message.reply_text("Stos is dead. 💀")
        await update.message.reply_text(f"Stos is alive. It took {elapsed_time} seconds to check.")

    @admin_only
    @prevent_edited
    async def _screenshot(self, update: Update, context) -> None:
        """ Take a screenshot of a page """
        args, _ = self._get_args(context)
        if not args:
            await update.message.reply_text("Please provide a url.")
            return
        url = args[0]
        await update.message.reply_text("Taking a screenshot...")
        image = await self._miscelanious_module.screenshot(url)
        await update.message.reply_photo(image)

    def prepare(self) -> bool:
        self._miscelanious_module = self._telebot_module.get_dsb_module("Miscelanious")
        if not self._miscelanious_module:
            self._telebot_module.log("ERROR", "Miscelanious module not found.")
            return False
        return True
