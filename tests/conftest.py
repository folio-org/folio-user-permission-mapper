import logging
import time

import pytest
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
