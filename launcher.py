""" Launching file for the application. """

import os
import argparse
import subprocess
import signal
from dsb.gui import cli
from dsb.main.dsb_class import DSB

def argparser_setup() -> argparse.ArgumentParser:
    """ Setup the argument parser for the application. """
    argparser = argparse.ArgumentParser(description="DSB - DatSimonBot")
    argparser.add_argument("-e", "--experimental", action="store_true",
                           help="Switch to experimental modules")
    argparser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    argparser.add_argument("-s", "--stats", action="store_true",
                           help="Show usage statistics instead of GUI")
    argparser.add_argument("--silent", action="store_true", help="Disable GUI")
    return argparser

if __name__ == "__main__":
    parser = argparser_setup()
    args = parser.parse_args()

    dsb = DSB(args)

    app = cli.App(dsb)

    if os.name == "nt":
        with subprocess.Popen(["python", "-m", "dsb.telebot.telebot_module"],
                              shell=True) as telebot_process:
            try:
                app.run_app()
            finally:
                telebot_process.send_signal(signal.CTRL_BREAK_EVENT)
                telebot_process.terminate()
                telebot_process.wait()
    else:
        with subprocess.Popen(["python3", "-m", "dsb.telebot.telebot_module"],
                              shell=False) as telebot_process:
            try:
                app.run_app()
            finally:
                telebot_process.terminate()
                telebot_process.wait()
