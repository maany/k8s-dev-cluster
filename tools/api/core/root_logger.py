import logging

def config_root_logger(verbosity):
    """
    Configure application logger based on verbosity level received from CLI
    Verbosity values of 0, 1, 2 correspond to log level of Warning, Info, Debug respectively
    :param verbosity: integer: 0, 1, 2
    """
    root_logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    api_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt='%d/%m/%Y %I:%M:%S %p')
    console_handler.setFormatter(formatter)
    if verbosity == 0:
        root_logger.setLevel(logging.WARNING)
    elif verbosity == 1:
        root_logger.setLevel(logging.INFO)
    elif verbosity >= 2:
        root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
