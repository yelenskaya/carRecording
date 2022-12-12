from logging import getLogger
from typing import BinaryIO

from boto3.resources.base import ServiceResource
from boto3.resources.model import Collection
from botocore.exceptions import ClientError
from botocore.response import StreamingBody

logger = getLogger(__name__)


class S3Error(Exception):
    pass


class S3FileNotFoundError(S3Error):
    pass


def get_file_object(resource: ServiceResource, bucket: str, object_key: str) -> StreamingBody:
    try:
        file = resource.Object(bucket, object_key).get()['Body']
    except ClientError as e:
        logger.error(f'Could not get file {object_key} from the bucket. Error: {e.response["Error"]}')
        if e.response['Error']['Code'] == 'NoSuchKey':
            raise S3FileNotFoundError(f'File with key {object_key} does not exist')
        raise S3Error
    return file


def get_all_object_summaries(resource: ServiceResource, bucket: str) -> Collection:
    try:
        summaries = resource.Bucket(bucket).objects.all()
    except ClientError as e:
        logger.error(f'Failed to get recordings from S3\n{e.response["Error"]}')
        raise S3Error

    return summaries


def upload_file_object(resource: ServiceResource, bucket: str, file: BinaryIO, target_object_key: str):
    try:
        resource.Bucket(bucket).upload_fileobj(file, target_object_key)
    except ClientError as e:
        logger.error(f'Failed to upload recording to S3\n{e.response["Error"]}')
        raise S3Error
