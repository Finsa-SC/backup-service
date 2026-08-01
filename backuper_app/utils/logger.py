import logging, sys

def get_logger(name: str):
    logging.basicConfig(
        format="[%(levelname)s] %(asctime)s %(name)s %(lineno)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        level=logging.INFO,
    )

    return logging.getLogger(name)
