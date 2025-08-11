import logging

from minio import Minio
from testcontainers.minio import MinioContainer

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
