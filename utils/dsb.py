import telebot.async_telebot as async_telebot
import utils.planingModule as planingModule

class DSB:
    def __init__(self, token: str, start_args: dict[str, bool] | None = None) -> None:
        self._bot = async_telebot.AsyncTeleBot(token)
        
        self.activate_modules(start_args)

    def activate_modules(self, args) -> None:
        if not args["no_planing"]:
            self._planing_module = planingModule.PlaningModule(self._bot)
    
    async def run(self) -> None:
        """ runs the bot
        """
        await self._bot.polling(non_stop=True)