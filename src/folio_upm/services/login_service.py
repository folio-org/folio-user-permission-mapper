import os

from cachetools import TTLCache, cached

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.integrations.login_client import LoginClient
from folio_upm.utils import env, log_factory



class LoginService(metaclass=SingletonMeta):
    """Service for managing login tokens for Okapi and Eureka."""

    def __init__(self):
        self._log = log_factory.get_logger(__name__)
        self._log.debug("LoginService initialized.")
        self._login_client = LoginClient()

    @cached(cache=TTLCache(maxsize=10, ttl=env.get_okapi_token_ttl()))
    def get_okapi_token(self):
        username = os.getenv("ADMIN_USERNAME")
        password = os.getenv("ADMIN_PASSWORD")
        return self._login_client.login_as_admin(env.get_okapi_url(), username, password)

    @cached(cache=TTLCache(maxsize=10, ttl=env.get_okapi_token_ttl()))
    def get_eureka_token(self):
        username = os.getenv("EUREKA_ADMIN_USERNAME")
        password = os.getenv("EUREKA_ADMIN_PASSWORD")
        return self._login_client.login_as_admin(env.get_eureka_url(), username, password)
