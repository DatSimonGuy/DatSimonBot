import telebot.async_telebot as async_telebot

class DSB:
    def __init__(self, token: str, start_args: dict[str, bool] | None = None) -> None:
        self._bot = async_telebot.AsyncTeleBot(token)
        
        self.activate_modules(start_args)

    def activate_modules(self, args: dict[str, bool]) -> None:
        if not args.get("no_planing", False):
            import utils.modules.utility.planingModule as planingModule

            self._planing_module = planingModule.PlaningModule(self._bot)

        if not args.get("no_stickers", False):
            import utils.modules.utility.stickerModule as stickerModule

            self._sticker_module = stickerModule.StickerModule(self._bot)
        
        if not args.get("no_gifs", False):
            import utils.modules.utility.gifModule as gifModule

            self._gif_module = gifModule.GifModule(self._bot)
        
        if not args.get("no_contexto", False):
            import utils.modules.games.contextoModule as contextoModule

            self._contexto_module = contextoModule.ContextoModule(self._bot)
    
    async def run(self) -> None:
        """ runs the bot
        """
        await self._bot.polling(non_stop=True)