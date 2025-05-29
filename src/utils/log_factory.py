import logging
import os

_RESET = "\033[0m"
_COLORS = {
    'DEBUG': "\033[37m",
    'INFO': "\033[37m",
    'WARNING': "\033[97m",
    'ERROR': "\033[1;31m",
    'CRITICAL': "\033[1;31m"
}

_logLevel = None


class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_color = _COLORS.get(record.levelname, _RESET)
        message = super().format(record)
        return f"{log_color}{message}{_RESET}"


def _get_log_level():
    global _logLevel
    if _logLevel:
        return _logLevel
    _logLevel = os.getenv("LOG_LEVEL", "INFO").upper()
    if _logLevel not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise ValueError(f"Invalid LOG_LEVEL: {_logLevel}")
    return _logLevel


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(_get_log_level())
    console_handler = logging.StreamHandler()
    formatter = CustomFormatter('%(asctime)s %(levelname)-8s %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
