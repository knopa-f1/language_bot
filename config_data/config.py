from dotenv import find_dotenv, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = find_dotenv()
load_dotenv(env_path)


class DatabaseConfig(BaseSettings):
    host: str = Field(..., alias="DB_HOST")
    port: int = Field(..., alias="DB_PORT")
    user: str = Field(..., alias="DB_USER")
    password: str = Field(..., alias="DB_PASSWORD")
    name: str = Field(..., alias="DB_NAME")

    @property
    def dsn(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}" f"@{self.host}:{self.port}/{self.name}"


class RedisConfig(BaseSettings):
    host: str = Field("localhost", alias="REDIS_HOST")
    port: int = Field(6379, alias="REDIS_PORT")
    db: int = Field(0, alias="REDIS_DB")
    password: str | None = Field(None, alias="REDIS_PASSWORD")
    ttl: int = Field(3600, alias="REDIS_TTL")

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


class TgBot(BaseSettings):
    token: str = Field(..., alias="bot_token")


class ConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    tg_bot: TgBot = TgBot()
    db: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    env_type: str = Field("test", env="ENV_TYPE")
    timezone: int = Field(0, env="TIMEZONE")
    is_docker: bool = Field(False, env="IN_DOCKER")
