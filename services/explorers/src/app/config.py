from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    jwt_key: str = 'secret'
    mongo_uri: str = 'mongodb://localhost:27017'

    model_config = SettingsConfigDict(env_file="app.env")


@lru_cache
def get_settings():
    return Settings()
