import os
from functools import cache
from typing import Optional

import dotenv

from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.types.eureka_load_strategy import EurekaLoadStrategy
from folio_upm.utils import log_factory
from folio_upm.utils.utils import Utils


def load_dotenv():
    print("loading dotenv from upm_env.py...")
    custom_env = os.getenv("DOTENV")
    if custom_env:
        dotenv.load_dotenv(custom_env)
    dotenv.load_dotenv()


class Env(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("Env class initialized.")

    def get_okapi_url(self) -> str:
        return self.require_env_cached("OKAPI_URL", default_value="http://localhost:9130")

    def get_eureka_url(self) -> str:
        return self.require_env_cached("EUREKA_URL", default_value="http://kong:8000")

    def get_tenant_id(self) -> str:
        return self.require_env_cached("TENANT_ID")

    def get_s3_bucket(self) -> str:
        return self.require_env_cached("AWS_S3_BUCKET")

    def get_admin_username(self) -> str:
        return self.require_env_cached("ADMIN_USERNAME")

    def get_admin_password(self) -> str:
        return self.require_env_cached("ADMIN_PASSWORD", log_result=False)

    def get_http_client_timeout(self) -> int:
        default_timeout = 60
        request_timeout = self.require_env_cached("HTTP_CLIENT_TIMEOUT", default_value=str(default_timeout))
        if not request_timeout:
            return default_timeout
        return int(request_timeout)

    def get_bool_cached(self, env_variable_name: str, default_value: bool = False) -> bool:
        str_var = self.getenv_cached(env_variable_name, str(default_value))
        if str_var is None:
            self._log.debug("%s is not set, using default value: %s", env_variable_name, default_value)
            return default_value

        return Utils.parse_bool(str_var, default_value)

    def get_migration_strategy(self) -> EurekaLoadStrategy:
        resolved_strategy_name = self.getenv_cached("EUREKA_ROLE_LOAD_STRATEGY", default_value="distributed")
        eureka_load_strategy = EurekaLoadStrategy.from_string(resolved_strategy_name)
        if eureka_load_strategy is None:
            allowed_values = EurekaLoadStrategy.get_names()
            raise ValueError(f"Invalid role migration strategy provided. Allowed values are: {allowed_values}.")
        return eureka_load_strategy

    def get_enabled_storages(self) -> list[str]:
        storages = self.getenv_cached("ENABLED_STORAGES", default_value="s3")
        if not storages:
            raise ValueError("ENABLED_STORAGES environment variable is not set or empty.")

        parsed_storages = [x.strip() for x in storages.split(",")]
        allowed_values = {"s3", "local"}
        if not set(parsed_storages) <= allowed_values:
            raise ValueError(f"Invalid storages: '{parsed_storages}'. Allowed values are: {allowed_values}'.")
        return list(parsed_storages)

    @cache  # noqa: B019
    def getenv_cached(self, env_variable_name, default_value: str | None = None, log_result=True) -> Optional[str]:
        return self.getenv(env_variable_name, default_value, log_result)

    @cache  # noqa: B019
    def require_env_cached(self, env_variable_name, default_value=None, log_result=True) -> str:
        return self.require_env(env_variable_name, default_value, log_result)

    def require_env(self, env_variable_name, default_value=None, log_result=True) -> str:
        env_variable_value = os.getenv(env_variable_name, default_value)
        if not env_variable_value:
            raise ValueError(f"Environment variable is not set or empty: {env_variable_name}")
        if log_result:
            self._log.info(f"Resolved value for {env_variable_name}: {env_variable_value}")
        return env_variable_value

    def getenv(self, env_variable_name, default_value: Optional[str] = None, log_result=True) -> Optional[str]:
        env_variable_value = os.getenv(env_variable_name)
        if env_variable_value is None:
            self._log.debug(f"{env_variable_name} is not set, using default value: {default_value}")
            return default_value
        elif env_variable_value.strip() == "":
            self._log.debug(f"{env_variable_name} is set to an empty string, using default value: {default_value}")
            return default_value
        if log_result:
            self._log.info(f"Resolved value for {env_variable_name}: {env_variable_value}")
        return env_variable_value
