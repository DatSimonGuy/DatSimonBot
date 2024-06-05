import telebot.async_telebot as async_telebot

class DSB:
    def __init__(self, token: str, start_args: dict[str, bool] | None = None) -> None:
        self._bot = async_telebot.AsyncTeleBot(token)
        
        self.activate_modules(start_args)

    def activate_modules(self, args: dict[str, bool]) -> None:
        if not args.get("no_planing", False):
            import utils.modules.planingModule as planingModule

            self._planing_module = planingModule.PlaningModule(self._bot)
        if not args.get("no_stickers", False):
            import utils.modules.stickerModule as stickerModule

            self._sticker_module = stickerModule.StickerModule(self._bot)
    
    async def run(self) -> None:
        """ runs the bot
        """
        await self._bot.polling(non_stop=True)