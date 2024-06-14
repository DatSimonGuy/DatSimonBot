import telebot.async_telebot as async_telebot
from utils.modules.dsbModule import DsbModule

class DSB:
    def __init__(self, token: str, start_args: dict[str, bool] | None = None) -> None:
        self._bot = async_telebot.AsyncTeleBot(token)

        self.activate_modules(start_args)

    def _activate_module(self, module: DsbModule):
        self._activated_modules[module.__name__] = module(self._bot)

    def activate_modules(self, args: dict[str, bool]) -> None:
        self._activated_modules = {}

        self._avaible_modules = [
            ("no_planing", "utils.modules.utility.planingModule", "PlaningModule"),
            ("no_stickers", "utils.modules.utility.stickerModule", "StickerModule"),
            ("no_gifs", "utils.modules.utility.gifModule", "GifModule"),
            ("no_contexto", "utils.modules.games.contextoModule", "ContextoModule"),
            ("no_youtube", "utils.modules.utility.youtubeModule", "YoutubeModule"),
            ("", "utils.modules.utility.mainHandlerModule", "MainHandler")
        ]

        for arg, module_path, module_name in self._avaible_modules:
            if not args.get(arg, False):
                module = getattr(__import__(module_path, fromlist=[module_name]), module_name)
                self._activate_module(module)
    
    async def run(self) -> None:
        """ runs the bot
        """
        await self._bot.polling(non_stop=True)