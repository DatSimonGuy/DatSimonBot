import telebot.async_telebot as async_telebot
from utils.modules.dsbModule import DsbModule
import os
import sys
import time
import schedule
import threading
import logging

class DSB:
    def __init__(self, token: str, *args, **kwargs) -> None:
        self._bot = async_telebot.AsyncTeleBot(token)
        self._start_args = kwargs

        self._setup_moudules()
        
        self.__register_loggers()
        
        schedule_thread = threading.Thread(target=self._schedule_thread)
        schedule_thread.start()
    
    def __register_loggers(self):
        
        # Will redirect all logs to the DsbModule logger
        logger = logging.getLogger("TeleBot")
        logger.addHandler(DsbModule.LogHandler(self._activated_modules["DsbModule"].log_event))
        logger.setLevel(logging.ERROR)

        # Remove the original so it doesn't write to console
        logger.removeHandler(logger.handlers[0])

        # Allows the usage of print() and sys.stdout.write() to log events
        sys.stdout = DsbModule.StdoutWriter(self._activated_modules["DsbModule"].log_event)
        
        # Allows the usage of sys.stderr.write() to log events
        sys.stderr = DsbModule.StderrWriter(self._activated_modules["DsbModule"].log_event)
    
    def _schedule_thread(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def _setup_moudules(self):
        self._modules = []
        self._activated_modules: dict[str, DsbModule] = {"DsbModule": DsbModule(self._bot)} # That's a placeholder and error logger
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
            current_module = module(self._bot, **self._start_args)
            self._activated_modules[module.__name__] = current_module

            if not self._start_args.get(f"no_{module.__name__.split('Module')[0]}", False):
                self._activated_modules[module.__name__].set_state("active")
            else:
                self._activated_modules[module.__name__].set_state("disabled") 

    async def run(self) -> None:
        await self._bot.polling(non_stop=True)