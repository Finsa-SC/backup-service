import logging, sys
from logging import Logger, LogRecord

def configure_logging() -> None:
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        level=logging.INFO,
    )

    logging.getLogger("paramiko").setLevel(logging.WARNING)

def get_logger(name: str) -> Logger:
    return logging.getLogger(name)