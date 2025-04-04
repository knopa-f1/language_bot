from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv


env_path = find_dotenv()
load_dotenv(env_path)


class DatabaseConfig(BaseSettings):
    dsn: PostgresDsn = Field("", alias="DSN")


class StorageConfig(BaseSettings):
    redis_host: str = Field("", alias="REDIS_HOST")
    redis_port: str = Field("", alias="REDIS_PORT")
    redis_password: str = Field("", alias="REDIS_PASSWORD")


class TgBot(BaseSettings):
    token: str = Field(..., alias="bot_token")


class ConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    tg_bot: TgBot = TgBot()
    db: DatabaseConfig = DatabaseConfig()
    redis: StorageConfig = StorageConfig()
    env_type: str = Field("test", env="ENV_TYPE")
    timezone: int = Field(0, env="TIMEZONE")
