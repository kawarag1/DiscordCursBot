import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler


def setup_logger(log_directory="app/logs", level=logging.DEBUG):
    os.makedirs(log_directory, exist_ok=True)
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    current_date = time.strftime("%Y-%m-%d")
    log_file_path = os.path.join(log_directory, f"{current_date}.log")

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s")

    file_handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=30)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


logger = setup_logger()