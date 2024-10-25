from dataclasses import dataclass
from environs import Env
from pydantic import PostgresDsn


@dataclass
class DatabaseConfig:
    dsn: PostgresDsn


@dataclass
class StorageConfig:
    redis_host: str
    redis_port: str
    redis_password: str


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    redis: StorageConfig
    env_type: str


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  db=DatabaseConfig(
                      dsn=env('DNS')
                  ),
                  redis=StorageConfig(
                      redis_host=env('REDIS_HOST'),
                      redis_port=env('REDIS_PORT'),
                      redis_password=env('REDIS_PASSWORD')
                  ),
                  env_type=env('ENV_TYPE')
                  )
