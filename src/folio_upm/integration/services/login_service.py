import os

from cachetools import TTLCache, cached

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integration.clients.login_client import LoginClient
from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class LoginService(metaclass=SingletonMeta):
    """Service for managing login tokens for Okapi and Eureka."""

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("LoginService initialized.")
        self._login_client = LoginClient()

    @cached(cache=TTLCache(maxsize=10, ttl=os.getenv("ACCESS_TOKEN_TTL", 60)))
    def get_okapi_token(self):
        username = os.getenv("OKAPI_ADMIN_USERNAME")
        password = os.getenv("OKAPI_ADMIN_PASSWORD")
        return self._login_client.login_as_admin(Env().get_okapi_url(), username, password)

    @cached(cache=TTLCache(maxsize=10, ttl=os.getenv("ACCESS_TOKEN_TTL", 60)))
    def get_eureka_token(self):
        username = os.getenv("EUREKA_ADMIN_USERNAME")
        password = os.getenv("EUREKA_ADMIN_PASSWORD")
        return self._login_client.login_as_admin(Env().get_eureka_url(), username, password)
