import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def log(message):
    logger.info(message)