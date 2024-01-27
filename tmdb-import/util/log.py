import logging
import configparser
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8-sig')

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    if config.get("DEFAULT","logging_level", fallback="INFO").lower() == "debug": 
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger