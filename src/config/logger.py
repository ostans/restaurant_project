from loguru import logger

# import sys


""" remove the default logger """
logger.remove()


""" add a new logger that logs to stderr and a file with rotation and retention policies """
# logger.add(sys.stderr, format="{time} | {level} | {message}", level="DEBUG")
logger.add(
    "log/{time:YYYY-MM-DD}.log", rotation="00:00", retention="7 days", compression="zip"
)


""" We use the logger instance to log messages in our application. """
log = logger
