import os
import boto3
import dotenv
from utils import log_factory, env, json_utils
from botocore.exceptions import ClientError

dotenv.load_dotenv()

_log = log_factory.get_logger(__name__)
_s3_client = None


def init_client():
    region = env.require_env("AWS_REGION", default_value="us-east-1")
    endpoint = os.getenv("AWS_S3_ENDPOINT")
    if endpoint:
        _log.info(f"Initializing S3 client [awsRegion={region}, endpoint={endpoint}]...")
        return boto3.client('s3', region_name=region, endpoint_url=endpoint)
    _log.info(f"Initializing S3 client [awsRegion={region}]...")
    return boto3.client('s3', region_name=region)


def get_s3_client():
    global _s3_client
    if not _s3_client:
        _s3_client = init_client()
    return _s3_client


def upload_file(path, file_obj, content_type='application/json'):
    bucket = env.get_s3_bucket()
    file_exists = check_file_exists(path)
    if file_exists:
        _log.info(f"File already exists in S3 bucket '{bucket}': {path}")

    get_s3_client().upload_fileobj(file_obj, Bucket=bucket, Key=path)


def put_object(path, content, content_type='application/json'):
    bucket = env.get_s3_bucket()
    file_exists = check_file_exists(path)
    if file_exists:
        _log.info(f"File already exists in S3 bucket '{bucket}': {path}")
    _log.info(f"Writing JSON to S3 bucket '{bucket}': {path}")
    get_s3_client().put_object(
        Key=path,
        Body=content,
        Bucket=bucket,
        ContentEncoding='utf-8',
        ContentType=content_type)


def put_json_object(path, data):
    json_string = json_utils.to_json(data)
    put_object(path, json_string)


def check_file_exists(file):
    """
    Check if a file exists in an S3 bucket.
    :param bucket_name: Name of the S3 bucket
    :param file: Key (path) of the file in the bucket
    :return: True if the file exists, False otherwise
    """
    try:
        get_s3_client().head_object(Bucket=env.get_s3_bucket(), Key=file)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        raise


def read_json_object(file_key):
    bucket_name = env.get_s3_bucket()
    try:
        response = get_s3_client().get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')
        return json_utils.from_json(file_content)
    except Exception as e:
        _log.error(f"Error reading file '{file_key}' from bucket '{bucket_name}': {e}")
        raise ValueError("Failed to read JSON file from S3: "
                         f"bucker={bucket_name}, path={file_key}, error={e}")
