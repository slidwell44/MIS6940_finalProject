import logging


class FilterDebugMessages(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG
