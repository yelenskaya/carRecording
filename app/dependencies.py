from functools import lru_cache

from boto3 import resource
from redis.asyncio.client import Redis

from app.settings import Settings


@lru_cache
def get_settings():
    return Settings()


@lru_cache
def get_s3_resource():
    return resource('s3')


@lru_cache
def get_redis():
    _settings = get_settings()
    return Redis(host=_settings.REDIS_HOST, port=_settings.REDIS_PORT, db=_settings.REDIS_DB)
