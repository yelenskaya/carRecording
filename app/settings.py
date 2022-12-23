from pydantic import BaseSettings


class Settings(BaseSettings):
    S3_BUCKET: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        frozen = True
