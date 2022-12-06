from pydantic import BaseSettings


class Settings(BaseSettings):
    S3_BUCKET: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
