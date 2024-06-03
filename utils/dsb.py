import telebot.async_telebot as async_telebot
import utils.planingModule as planingModule

class DSB:
    def __init__(self, token: str) -> None:
        self.bot = async_telebot.AsyncTeleBot(token)
        self.planing_module = planingModule.PlaningModule(self.bot)
    
    async def run(self) -> None:
        await self.bot.polling(non_stop=True)