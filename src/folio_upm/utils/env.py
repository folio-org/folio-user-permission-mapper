import os
from functools import lru_cache, cache
from typing import Any, Optional

from folio_upm.utils import log_factory

_log = log_factory.get_logger(__name__)


def get_okapi_url():
    return require_env("OKAPI_URL", default_value="http://localhost:9130")


def get_eureka_url():
    return require_env("EUREKA_URL", default_value="http://kong:8000")


def get_tenant_id():
    return require_env("TENANT_ID")


def get_s3_bucket():
    return require_env("AWS_S3_BUCKET")


def get_admin_username():
    return require_env("ADMIN_USERNAME")


def get_admin_password():
    return require_env("ADMIN_PASSWORD", log_result=False)


def get_okapi_token_ttl():
    return int(require_env("OKAPI_TOKEN_TTL", default_value="600", log_result=False))


def get_eureka_token_ttl():
    return int(require_env("OKAPI_EUREKA_TTL", default_value="600", log_result=False))


def get_http_client_timeout():
    return int(require_env("HTTP_CLIENT_TIMEOUT", default_value="60", log_result=False))


@cache
def get_env(env_variable_name, default_value: str | None = None, log_result=True) -> Optional[str]:
    env_variable_value = os.getenv(env_variable_name, default_value)
    if log_result:
        _log.info(f"Resolved value for {env_variable_name}: {env_variable_value}")
    return env_variable_value


@cache
def require_env(env_variable_name, default_value=None, log_result=True) -> str:
    env_variable_value = os.getenv(env_variable_name, default_value)
    if not env_variable_value:
        raise ValueError(f"{env_variable_name} is not set")
    if log_result:
        _log.info(f"Resolved value for {env_variable_name}: {env_variable_value}")
    return env_variable_value
