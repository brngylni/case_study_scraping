import logging
import os
from collections.abc import Mapping
from logging.handlers import RotatingFileHandler
from pprint import pformat

import coloredlogs


class PrettyDictFormatter(logging.Formatter):
    def format(self, record):
        # Check if the message is a Mapping (e.g., dict, DynamoDB AttributeDict)
        if isinstance(record.msg, Mapping):
            # Pretty-print dictionary-like objects
            record.msg = pformat(dict(record.msg), indent=4, width=120)
        return super().format(record)


def setup_logger(module_name, level=logging.DEBUG):
    """
    Sets up a logger for a specific module with file, console (colored), and CloudWatch handlers.
    Ensures UTF-8 encoding and formats dictionaries for readability.
    """
    # Determine the root and logs directory dynamically
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOGS_DIR = os.path.join(ROOT_DIR, "logs")
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Create a logger
    logger = logging.getLogger(module_name)

    # Clear existing handlers to prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)
    logger.propagate = False  # Avoid duplicate logs from propagation

    # Custom formatter for all handlers
    formatter = PrettyDictFormatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler with UTF-8 encoding
    log_file = os.path.join(LOGS_DIR, f"{module_name.split('.')[0]}.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    coloredlogs.install(
        level=logging.INFO,
        logger=logger,
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Add file handler to the logger
    logger.addHandler(file_handler)

    return logger
