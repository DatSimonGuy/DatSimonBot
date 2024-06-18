import telebot.async_telebot as async_telebot
from utils.modules.dsbModule import DsbModule
import os

class DSB:
    def __init__(self, token: str, start_args: dict | None = None) -> None:
        self._bot = async_telebot.AsyncTeleBot(token)
        self._start_args = start_args
        self._setup_moudules()
        
    def _setup_moudules(self):
        self._modules = []
        self._activated_modules: dict[str, DsbModule] = {}
        list_of_modules = []
        for dir in os.listdir("utils/modules/"):
            if not os.path.isdir(f"utils/modules/{dir}"):
                continue
            if dir.startswith("__"):
                continue
            for name in os.listdir(f"utils/modules/{dir}"):
                if not "Module" in name:
                    continue
                module_name = name.replace(".py", "")
                list_of_modules.append((f"utils.modules.{dir}.{module_name}", module_name[0].upper() + module_name[1:]))
        
        for path, name in list_of_modules:
            module = getattr(__import__(path, fromlist=[name]), name)
            
            if not module.used:
                continue
            
            self._modules.append(module)
        
        for module in self._modules:
            current_module = module(self._bot)
            self._activated_modules[module.__name__] = current_module

            if not self._start_args.get(f"no_{module.__name__.split('Module')[0]}", False):
                self._activated_modules[module.__name__].set_state("active")
            else:
                self._activated_modules[module.__name__].set_state("disabled") 

    
    async def run(self) -> None:
        await self._bot.polling(non_stop=True)