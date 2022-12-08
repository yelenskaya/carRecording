from functools import lru_cache

from boto3 import resource
from fastapi import Depends

from app.settings import Settings


@lru_cache
def get_settings():
    return Settings()


@lru_cache
def get_s3_resource():
    return resource('s3')


@lru_cache
def get_s3_bucket(s3_resource=Depends(get_s3_resource), settings=Depends(get_settings)):
    return s3_resource.Bucket(settings.S3_BUCKET)
