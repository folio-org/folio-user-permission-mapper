from io import BytesIO
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_s3 import S3Client

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.utils import log_factory
from folio_upm.utils.file_utils import FileUtils
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.upm_env import Env


class S3Storage(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._bucket = Env().get_s3_bucket()
        self._s3_client = self.__init_client()
        self._log.debug("S3Client initialized.")

    def upload_file(self, path, file_obj: BytesIO, override: bool = True):
        file_obj.seek(0)
        bucket = self._bucket
        file_exists = self.check_file_exists(path)
        if file_exists:
            self._log.warn("Object exists in S3 bucket '%s': %s, overriding it", bucket, path)
            if not override:
                raise FileExistsError(f"File already exists in S3 bucket '{bucket}': {path}")
        self._s3_client.upload_fileobj(file_obj, Bucket=bucket, Key=path)

    def check_file_exists(self, file):
        try:
            self._s3_client.head_object(Bucket=self._bucket, Key=file)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def read_json_object(self, file_key) -> dict:
        file_content = self.__get_object(file_key).read().decode("utf-8")
        return JsonUtils.from_json(file_content)

    def read_object(self, file_key):
        if not self.check_file_exists(file_key):
            return None

        return self.__get_object(file_key)

    def find_latest_key_by_prefix(self, prefix: str) -> Optional[str]:
        try:
            paginator = self._s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=self._bucket, Prefix=prefix)

            matching_keys = []
            for page in page_iterator:
                for obj in page.get("Contents", []):
                    matching_keys.append(obj["Key"])

            if not matching_keys:
                self._log.debug(f"No files found with prefix: {prefix}")
                return None

            latest_key = FileUtils.get_latest_file_key(matching_keys)
            self._log.debug(f"Found files with prefix '{prefix}', latest: {latest_key}, files: {matching_keys}")
            return latest_key

        except Exception as e:
            self._log.error("Error finding latest file with prefix '%s'", prefix, e)
            return None

    def __get_object(self, file_key):
        bucket_name = self._bucket
        try:
            response = self._s3_client.get_object(Bucket=bucket_name, Key=file_key)
            return response["Body"]
        except Exception as e:
            self._log.warn("Error reading file '%s' from bucket '%s'", file_key, bucket_name, e)
            raise ValueError("Failed to read JSON file from S3: " f"bucker={bucket_name}, path={file_key}, error={e}")

    def __init_client(self) -> S3Client:
        region = Env().require_env("AWS_REGION", default_value="us-east-1")
        endpoint = Env().get_env("AWS_S3_ENDPOINT")
        if endpoint:
            self._log.info(f"Initializing S3 client [awsRegion={region}, endpoint={endpoint}]...")
            return boto3.client("s3", region_name=region, endpoint_url=endpoint)
        self._log.info(f"Initializing S3 client [awsRegion={region}]...")
        return boto3.client("s3", region_name=region)
