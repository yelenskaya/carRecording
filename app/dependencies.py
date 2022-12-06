from functools import lru_cache

from boto3 import client

from app.settings import Settings


@lru_cache
def get_settings():
    return Settings()


@lru_cache
def get_s3_client():
    return client('s3')
