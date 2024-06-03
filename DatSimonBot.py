import os
from dotenv import load_dotenv
import argparse
from utils.dsb import DSB
import asyncio

argparser = argparse.ArgumentParser()

if __name__ == "__main__":
    load_dotenv()

    token = os.getenv('BOT_TOKEN')

    dsb = DSB(token)
    asyncio.run(dsb.run())