import json
import logging
from io import BytesIO
from typing import Generator, Any

from minio import Minio
from testcontainers.minio import MinioContainer

from folio_upm.utils.json_utils import JsonUtils

_log = logging.getLogger(__name__)


class MinioTestHelper:

    @staticmethod
    def get_container():
        container = MinioContainer(image="quay.io/minio/minio")
        container.with_command("server /data --console-address :9001")
        container.with_env("MINIO_ROOT_USER", "minioadmin")
        container.with_env("MINIO_ROOT_PASSWORD", "minioadmin")
        return container

    @staticmethod
    def get_base_url(minio: MinioContainer):
        return minio.get_config().get("endpoint")

    @staticmethod
    def create_bucket(minio_client: Minio, bucket_name: str):
        minio_client.make_bucket(bucket_name)

    @staticmethod
    def delete_bucket(minio_client: Minio, bucket_name: str):
        minio_client.remove_bucket(bucket_name)

    @staticmethod
    def create_test_minio_client(minio_container) -> Minio:
        return minio_container.get_client()

    @staticmethod
    def with_jsongz_object(minio_client: Minio, bucket_name: str, object_key: str, value: Any) -> Generator[str, None, None]:
        json_data = JsonUtils().to_json_gz(value)
        json_data.seek(0)
        minio_client.put_object(
            bucket_name,
            object_key,
            json_data,
            length=json_data.getbuffer().nbytes,
            content_type="application/json",
        )
        yield object_key
        minio_client.remove_object(bucket_name, object_key)
