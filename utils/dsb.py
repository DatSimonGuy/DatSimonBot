import telebot.async_telebot as async_telebot

class DSB:
    def __init__(self, token: str, start_args: dict[str, bool] | None = None) -> None:
        self._bot = async_telebot.AsyncTeleBot(token)
        
        self.activate_modules(start_args)

    def activate_modules(self, args: dict[str, bool]) -> None:
        modules = [
            ("no_planing", "utils.modules.utility.planingModule", "PlaningModule"),
            ("no_stickers", "utils.modules.utility.stickerModule", "StickerModule"),
            ("no_gifs", "utils.modules.utility.gifModule", "GifModule"),
            ("no_contexto", "utils.modules.games.contextoModule", "ContextoModule"),
            ("no_youtube", "utils.modules.utility.youtubeModule", "YoutubeModule"),
            ("", "utils.modules.utility.mainHandlerModule", "MainHandler")
        ]

        for arg, module_path, module_name in modules:
            if not args.get(arg, False):
                module = getattr(__import__(module_path, fromlist=[module_name]), module_name)
                module(self._bot)
    
    async def run(self) -> None:
        """ runs the bot
        """
        await self._bot.polling(non_stop=True)