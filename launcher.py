""" Launching file for the application. """

import argparse
from gui import cli_gui
from dsb_main.dsb import DSB

def argparser_setup() -> argparse.ArgumentParser:
    """ Setup the argument parser for the application. """
    argparser = argparse.ArgumentParser(description="DSB - DatSimonBot")
    argparser.add_argument("-e", "--experimental", action="store_true",
                           help="Switch to experimental modules")
    argparser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    return argparser

if __name__ == "__main__":
    parser = argparser_setup()
    args = parser.parse_args()

    dsb = DSB(args)

    app = cli_gui.App(dsb)

    app.run_app()
