import logging
import os
from functools import cache

from folio_upm.utils import upm_env

_RESET = "\033[0m"
_COLORS = {
    "DEBUG": "\033[90m",
    "INFO": "\033[37m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
    "CRITICAL": "\033[1;31m",
}

upm_env.load_dotenv()


@cache
def _get_tenant_id():
    tenant_id = os.getenv("TENANT_ID")
    if not tenant_id:
        raise ValueError("TENANT_ID environment variable is not set")
    return tenant_id


@cache
def _get_log_level():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if log_level not in logging.getLevelNamesMapping():
        raise ValueError(f"Invalid LOG_LEVEL: {log_level}")
    return log_level


class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None):
        super().__init__(fmt or "[%(asctime)s] [%(levelname)-8s] [%(shortname)-30s] %(message)s")

    def format(self, record):
        log_color = _COLORS.get(record.levelname, _RESET)
        record.shortname = record.name[-30:]
        message = super().format(record)
        return f"{log_color}[{_get_tenant_id()}] {message}{_RESET}"


def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        log_level = _get_log_level()
        logger.setLevel(log_level)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(CustomFormatter())
        logger.addHandler(console_handler)
    return logger
