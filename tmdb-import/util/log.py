import logging

def setup_custom_logger(name, debug_mode=False):
    level = logging.DEBUG if debug_mode else logging.INFO

    # Reconfigure root logger each run so CLI flags (-d/--debug) always win.
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        force=True,
    )

    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger