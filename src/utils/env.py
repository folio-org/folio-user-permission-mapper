import os

from utils import log_factory

_log = log_factory.get_logger(__name__)

_okapi_url = None
_s3_bucket = None
_tenant_id = None


def get_okapi_url():
    global _okapi_url
    if not _okapi_url:
        _okapi_url = require_env("OKAPI_URL", default_value="http://localhost:9130")
    return _okapi_url


def get_tenant_id():
    global _tenant_id
    if not _tenant_id:
        _tenant_id = require_env("TENANT_ID")
    return _tenant_id


def get_s3_bucket():
    global _s3_bucket
    if not _s3_bucket:
        _s3_bucket = require_env("AWS_S3_BUCKET")
    return _s3_bucket


def get_ids_partition_size():
    return int(require_env("PERMISSION_IDS_PARTITION_SIZE", default_value=50))

def get_admin_username():
    return require_env("ADMIN_USERNAME")


def get_admin_password():
    return require_env("ADMIN_PASSWORD", log_result=False)


def get_env(env_variable_name, default_value, log_result=True):
    env_variable_value = os.getenv(env_variable_name, default_value)
    if log_result:
        _log.info(f"Resolved value for {env_variable_name}: {env_variable_value}")
    return env_variable_value


def require_env(env_variable_name, default_value=None, log_result=True):
    env_variable_value = os.getenv(env_variable_name, default_value)
    if not env_variable_value:
        raise ValueError(f"{env_variable_name} is not set")
    if log_result:
        _log.info(f"Resolved value for {env_variable_name}: {env_variable_value}")
    return env_variable_value
