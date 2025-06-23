import boto3
from botocore.exceptions import ClientError
from mypy_boto3_s3 import S3Client

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.utils import env, json_utils, log_factory

_log = log_factory.get_logger(__name__)
_s3_client = None


class UpmS3Client(metaclass=SingletonMeta):

    def __init__(self):
        _log.debug("S3Client initialized.")
        self._bucket = env.get_s3_bucket()
        self._s3_client = UpmS3Client.__init_client()

    def upload_file(self, path, file_obj):
        bucket = self._bucket
        file_exists = self.check_file_exists(path)
        if file_exists:
            _log.info(f"File already exists in S3 bucket '{bucket}': {path}")

        self._s3_client.upload_fileobj(file_obj, Bucket=bucket, Key=path)

    def put_json_object(self, path, data):
        json_string = json_utils.to_json(data)
        self.__put_object(path, json_string)

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
        return json_utils.from_json(file_content)

    def read_json_gz_object(self, file_key) -> dict | None:
        if not self.check_file_exists(file_key):
            _log.info(f"File not found in S3 bucket '{self._bucket}': {file_key}")
            return None

        file_content = self.__get_object(file_key)
        return json_utils.from_gz_json(file_content)

    def __get_object(self, file_key):
        _log.info(f"Retrieving object from S3: {file_key}...")
        bucket_name = self._bucket
        try:
            response = self._s3_client.get_object(Bucket=bucket_name, Key=file_key)
            return response["Body"]
        except Exception as e:
            _log.error(f"Error reading file '{file_key}' from bucket '{bucket_name}': {e}")
            raise ValueError("Failed to read JSON file from S3: " f"bucker={bucket_name}, path={file_key}, error={e}")

    def __put_object(self, path, content, content_type="application/json"):
        bucket = self._bucket
        file_exists = self.check_file_exists(path)
        if file_exists:
            _log.info(f"File already exists in S3 bucket '{bucket}': {path}")
        _log.info(f"Writing JSON to S3 bucket '{bucket}': {path}")
        self._s3_client.put_object(
            Key=path,
            Body=content,
            Bucket=bucket,
            ContentEncoding="utf-8",
            ContentType=content_type,
        )

    @staticmethod
    def __init_client() -> S3Client:
        region = env.require_env("AWS_REGION", default_value="us-east-1")
        endpoint = env.find_env("AWS_S3_ENDPOINT")
        if endpoint:
            _log.info(f"Initializing S3 client [awsRegion={region}, endpoint={endpoint}]...")
            return boto3.client("s3", region_name=region, endpoint_url=endpoint)
        _log.info(f"Initializing S3 client [awsRegion={region}]...")
        return boto3.client("s3", region_name=region)
