import os
from functools import lru_cache
from typing import Optional

import dotenv

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.utils import log_factory
from folio_upm.utils.service_utils import ServiceUtils


def load_dotenv():
    print("loading dotenv from upm_env.py...")
    dotenv.load_dotenv()
    dotenv.load_dotenv()
    dotenv.load_dotenv(os.getenv("DOTENV", ".env"), override=True)


class Env(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("Env class initialized.")

    def get_okapi_url(self):
        return self.require_env("OKAPI_URL", default_value="http://localhost:9130")

    def get_eureka_url(self):
        return self.require_env("EUREKA_URL", default_value="http://kong:8000")

    def get_tenant_id(self):
        return self.require_env("TENANT_ID")

    def get_s3_bucket(self):
        return self.require_env("AWS_S3_BUCKET")

    def get_admin_username(self):
        return self.require_env("ADMIN_USERNAME")

    def get_admin_password(self):
        return self.require_env("ADMIN_PASSWORD", log_result=False)

    def get_http_client_timeout(self):
        return int(self.require_env("HTTP_CLIENT_TIMEOUT", default_value="60", log_result=False))

    def get_bool(self, env_variable_name: str, default_value: bool = False) -> bool:
        str_var = self.get_env(env_variable_name, str(default_value))
        return ServiceUtils.parse_bool(str_var, default_value)

    @lru_cache(maxsize=100)
    def get_env(self, env_variable_name, default_value: str | None = None, log_result=True) -> Optional[str]:
        env_variable_value = os.getenv(env_variable_name, default_value)
        if log_result:
            self._log.info(f"Resolved value for {env_variable_name}: {env_variable_value}")
        return env_variable_value

    @lru_cache(maxsize=100)
    def require_env(self, env_variable_name, default_value=None, log_result=True) -> str:
        env_variable_value = os.getenv(env_variable_name, default_value)
        if not env_variable_value:
            raise ValueError(f"{env_variable_name} is not set")
        if log_result:
            self._log.info(f"Resolved value for {env_variable_name}: {env_variable_value}")
        return env_variable_value
