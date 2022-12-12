from functools import lru_cache

from boto3 import resource

from app.settings import Settings


@lru_cache
def get_settings():
    return Settings()


@lru_cache
def get_s3_resource():
    return resource('s3')
