import getopt
import platform
import logging
import os
import sys
from .version import script_name, __version__
from .util.log import setup_custom_logger
import re

setup_custom_logger('root')

_options = [
    'help',
    'version',
]

_short_options = 'hV'

_help = f"Usage: {script_name} [OPTION]... [URL]..."

def main(**kwargs):
    logging.debug(f'Welcome to {script_name}')
    opts = {}
    args = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], _short_options, _options)
    except getopt.GetoptError as e:
        logging.error(f"Invalid option! Try {script_name} --help' for more options.")

    if not opts and not args:
        print(_help)
    else:
        conf = {}
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                # Display help.
                print(_help)
            elif opt in ('-V', '--version'):
                # Display version.
                print("tmdb-import:")
                print("    version:  {}".format(__version__))
                print("    platform: {}".format(platform.platform()))
                print("    python:   {}".format(sys.version.split('\n')[0]))
        
    if args:
        if args[0].lower() in ("backdrop", "poster"):
            from .processor import process_image_from_url
            process_image_from_url(args[0].lower(), args[1])
        elif args[0].lower() == "fitsize":
            print(args[1])
            fitsize = re.split('_|-|\*', args[1])
            from .processor import process_image_from_url
            process_image_from_url(args[0].lower(), args[2], int(fitsize[0]), int(fitsize[1]))
        elif args[0].__contains__("www.themoviedb.org"):
            from .importor import import_from_url
            import_from_url(args[0])
        else:
            from .extractor import extract_from_url
            extract_from_url(args[0])

if __name__ == '__main__':
    main()