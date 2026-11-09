import logging
from typing import Any, Dict, Generator

import boto3
from testcontainers.core.container import DockerContainer

from folio_upm.utils.json_utils import JsonUtils

_log = logging.getLogger(__name__)

_S3_PORT = 8333


class SeaweedFsContainer(DockerContainer):
    """S3-compatible test container backed by SeaweedFS (Apache 2.0)."""

    access_key = "test-access-key"
    secret_key = "test-secret-key"
    region = "us-east-1"

    def __init__(self, image: str = "chrislusf/seaweedfs:latest"):
        super().__init__(image)
        self.with_command(f"server -s3 -s3.port={_S3_PORT} -dir=/data")
        self.with_exposed_ports(_S3_PORT)

    def get_config(self) -> Dict[str, str]:
        endpoint = f"{self.get_container_host_ip()}:{self.get_exposed_port(_S3_PORT)}"
        return {"endpoint": endpoint, "access_key": self.access_key, "secret_key": self.secret_key}

    def get_client(self):
        config = self.get_config()
        return boto3.client(
            "s3",
            endpoint_url=f"http://{config['endpoint']}",
            aws_access_key_id=config["access_key"],
            aws_secret_access_key=config["secret_key"],
            region_name=self.region,
        )


class MinioTestHelper:

    @staticmethod
    def get_container() -> SeaweedFsContainer:
        return SeaweedFsContainer()

    @staticmethod
    def put_jsongz_object(s3_client, bucket_name: str, object_key: str, value: Any) -> Generator[str, None, None]:
        json_data = JsonUtils().to_json_gz(value)
        json_data.seek(0)
        s3_client.put_object(
            Bucket=bucket_name, Key=object_key, Body=json_data.getvalue(), ContentType="application/json"
        )
        yield object_key
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
