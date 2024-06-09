import os
from dotenv import load_dotenv
import argparse
from utils.dsb import DSB
import asyncio

if __name__ == "__main__":
    load_dotenv()

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--no-planing", help="disable the planing module", action="store_true")
    argparser.add_argument("--no-stickers", help="disable the sticker module", action="store_true")
    argparser.add_argument("--no-gifs", help="disable the gif module", action="store_true")    
    argparser.add_argument("--no-contexto", help="disable the contexto module", action="store_true")

    args = vars(argparser.parse_args())

    token = os.getenv('BOT_TOKEN')

    dsb = DSB(token, args)
    asyncio.run(dsb.run())