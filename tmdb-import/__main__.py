import getopt
import platform
import logging
import os
import sys
from .version import script_name, __version__

_options = [
    'help',
    'version',
    'force',
]

_short_options = 'hVf'

_help = f"Usage: {script_name} [OPTION]... [URL]..."

def main(**kwargs):
    try:
        opts, args = getopt.getopt(sys.argv[1:], _short_options, _options)
    except getopt.GetoptError as e:
        logging.error(f"Invalid option! Try {script_name} --help' for more options.")

    if not opts and not args:
        # Display help.
        print(_help)
        # Enter GUI mode.
        #from .gui import gui_main
        #gui_main()
    else:
        conf = {}
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                # Display help.
                print(_help)
            elif opt in ('-V', '--version'):
                # Display version.
                print("tmdb-import:")
                print(f"    Version:  {__version__}")
                print(f"    platform: {platform.platform()}")
                print(f"    python:   {sys.version.split('\n')[0]}")

if __name__ == '__main__':
    main()