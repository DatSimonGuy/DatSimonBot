""" Launching file for the application. """

import argparse
from GUI import tkinter_gui as tk_gui
from DSB.dsb import DSB

def argparser_setup() -> argparse.ArgumentParser:
    """ Setup the argument parser for the application. """
    argparser = argparse.ArgumentParser(description="DSB - DatSimonBot")
    argparser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    return argparser

if __name__ == "__main__":
    parser = argparser_setup()
    args = parser.parse_args()
    
    app = tk_gui.App()

    dsb = DSB("stable")

    app.set_functions(dsb.run, dsb.stop, args, dsb.get_status)

    app.run_app()
    