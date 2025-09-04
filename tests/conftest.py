import logging
import os
import time
from typing import Dict, Generator

import pytest
from wiremock.resources.mappings import Mapping

from minio_test_helper import MinioTestHelper  # type: ignore[import-error]
from wiremock.constants import Config
from wiremock_test_helper import WireMockTestHelper  # type: ignore[import-error]

from folio_upm.model.cls_support import SingletonMeta

logging.getLogger("testcontainers").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("docker").setLevel(logging.WARNING)
logging.getLogger("s3transfer").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)


# noinspection PyProtectedMember
@pytest.fixture(scope="class")
def clear_singletons():
    SingletonMeta._instances.clear()
    yield
    SingletonMeta._instances.clear()


@pytest.fixture(scope="module")
def wiremock_container():
    """Setup WireMock server for testing using testcontainers"""
    container = WireMockTestHelper.get_container()
    with container as wiremock:
        Config.base_url = wiremock.get_url("__admin")
        yield wiremock


@pytest.fixture(scope="function")
def wiremock_url(wiremock_container):
    return wiremock_container.get_url("")


@pytest.fixture(scope="module")
def minio_container():
    """Set the base URL for WireMock"""
    with MinioTestHelper.get_container() as minio_container:
        client = minio_container.get_client()
        max_retries = 10
        for attempt in range(max_retries):
            try:
                client.list_buckets()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1)
        yield minio_container


@pytest.fixture(scope="module")
def minio_client(minio_container):
    yield minio_container.get_client()


@pytest.fixture(scope="function")
def test_s3_bucket(minio_client):
    bucket_name = "test-bucket"
    minio_client.make_bucket(bucket_name)
    yield bucket_name

    objects = minio_client.list_objects(bucket_name, recursive=True)
    for obj in objects:
        minio_client.remove_object(bucket_name, obj.object_name)
    minio_client.remove_bucket(bucket_name)


@pytest.fixture(scope="function")
def test_tenant_id() -> Generator[str, None, None]:
    yield "test_tenant"


@pytest.fixture(scope="function")
def test_tenant_env(test_tenant_id) -> Generator[Dict[str, str], None, None]:
    yield from with_env_variables({"TENANT_ID": test_tenant_id})


@pytest.fixture(scope="function")
def eureka_role_load_strategy_env() -> Generator[Dict[str, str], None, None]:
    yield from with_env_variables({"EUREKA_ROLE_LOAD_STRATEGY": "distributed"})


@pytest.fixture(scope="function", autouse=False)
def eureka_login_http_mock() -> Generator[Mapping, None, None]:
    yield from WireMockTestHelper.set_mapping("mod-login/eureka-login-success.json")


@pytest.fixture(scope="function", autouse=False)
def okapi_login_http_mock() -> Generator[Mapping, None, None]:
    yield from WireMockTestHelper.set_mapping("mod-login/okapi-login-success.json")


@pytest.fixture(scope="function")
def s3_environment(minio_container, test_s3_bucket) -> Generator[Dict[str, str], None, None]:
    minio_config = minio_container.get_config()
    yield from with_env_variables(
        {
            "STORAGE_TYPE": "s3",
            "AWS_S3_ENDPOINT": f"http://{minio_config.get("endpoint")}",
            "AWS_S3_BUCKET": test_s3_bucket,
            "AWS_S3_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": minio_config.get("access_key"),
            "AWS_SECRET_ACCESS_KEY": minio_config.get("secret_key"),
        }
    )


@pytest.fixture(scope="function")
def eureka_wiremock_env(wiremock_container):
    yield from with_env_variables(
        {
            "EUREKA_URL": wiremock_container.get_url(""),
            "EUREKA_ADMIN_USERNAME": "test_eureka_admin",
            "EUREKA_ADMIN_PASSWORD": "test_eureka_password",
        }
    )


@pytest.fixture(scope="function")
def okapi_wiremock_env(wiremock_container):
    yield from with_env_variables(
        {
            "OKAPI_URL": wiremock_container.get_url(""),
            "OKAPI_ADMIN_USERNAME": "test_okapi_admin",
            "OKAPI_ADMIN_PASSWORD": "test_okapi_password",
        }
    )


def with_env_variables(env_variables: Dict[str, str]) -> Generator[Dict[str, str], None, None]:
    for env_var_key, env_var_value in env_variables.items():
        os.environ[env_var_key] = env_var_value
    yield env_variables
    for var in env_variables:
        if var in os.environ:
            del os.environ[var]
