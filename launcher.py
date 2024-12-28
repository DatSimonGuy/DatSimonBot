""" Launching file for the application. """

from dsb.engine import DSBEngine

if __name__ == "__main__":
    dsb = DSBEngine()
    dsb.start()
