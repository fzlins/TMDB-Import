import getopt
import platform
import logging
import os
import sys
from .version import script_name, __version__
from .util.log import setup_custom_logger
import re

_options = [
    'help',
    'version',
    'debug',
    'headless',
]

_short_options = 'hVd'

_help = f"""Usage: {script_name} [OPTION]... [URL]...

Options:
  -h, --help       Show this help message and exit
  -V, --version    Show version information
  -d, --debug      Enable debug logging (default: INFO level)
      --headless   Run browser in headless mode (default: GUI mode)

Examples:
  {script_name} "http://www.example.com/video.html"
  {script_name} -d "https://www.themoviedb.org/tv/203646/season/1?language=zh-CN"
  {script_name} --headless --debug backdrop "https://www.example.com/image.jpg"
  {script_name} -d --headless "http://www.example.com/video.html"
"""

def main(**kwargs):
    opts = {}
    args = {}
    debug_mode = False
    headless_mode = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], _short_options, _options)
    except getopt.GetoptError as e:
        print(f"Invalid option! Try '{script_name} --help' for more options.")
        return

    # Check for options first
    for opt, arg in opts:
        if opt in ('-d', '--debug'):
            debug_mode = True
        elif opt in ('--headless',):
            headless_mode = True
    
    # Setup logger with debug mode
    setup_custom_logger('root', debug_mode)
    logging.debug(f'Welcome to {script_name}')
    
    # Set global headless mode for the session
    os.environ['TMDB_HEADLESS_MODE'] = str(headless_mode)
    logging.debug(f'Headless mode: {headless_mode}')

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
            elif opt in ('-d', '--debug'):
                # Debug option already handled above
                pass
            elif opt in ('--headless',):
                # Headless option already handled above
                pass
        
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