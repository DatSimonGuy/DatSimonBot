""" Launching file for the application. """

from dsb.dsb import DSB

if __name__ == "__main__":
    dsb = DSB(module_src="dsb/modules/", experimental=True)
    dsb.run()
