""" Launching file for the application. """

import sys
import argparse
from dsb.gui import cli
from dsb.main.dsb import DSB

def argparser_setup() -> argparse.ArgumentParser:
    """ Setup the argument parser for the application. """
    argparser = argparse.ArgumentParser(description="DSB - DatSimonBot")
    argparser.add_argument("-e", "--experimental", action="store_true",
                           help="Switch to experimental modules")
    argparser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    argparser.add_argument("--telebot", action="store_true", help="Launch telebot only")
    return argparser

if __name__ == "__main__":
    parser = argparser_setup()
    args = parser.parse_args()

    dsb = DSB(args)

    if args.telebot:
        dsb.start_telebot()
        sys.exit(0)

    app = cli.App(dsb)

    app.run_app()
