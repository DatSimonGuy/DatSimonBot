import os
from dotenv import load_dotenv
import argparse
from utils.dsb import DSB
import asyncio

if __name__ == "__main__":
    load_dotenv()

    argparser = argparse.ArgumentParser()

    opts = [
        ("--no-planing", "disable the planing module"),
        ("--no-sticker", "disable the sticker module"),
        ("--no-gif", "disable the gif module"),
        ("--no-contexto", "disable the contexto module"),
        ("--no-youtube", "disable the youtube module"),
        ("--data-saving", "decrease data usage")
    ]

    for opt in opts:
        argparser.add_argument(opt[0], help=opt[1], action="store_true")

    args = vars(argparser.parse_args())

    token = os.getenv('BOT_TOKEN')

    dsb = DSB(token, **args)
    asyncio.run(dsb.run())