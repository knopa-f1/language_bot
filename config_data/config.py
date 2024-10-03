from dataclasses import dataclass
from environs import Env

from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    database: str
    db_host: str
    db_user: str
    db_password: str
    dp_port: str


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig

def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  db=DatabaseConfig(
                      database=env('DATABASE'),
                      db_host=env('DB_HOST'),
                      db_user=env('DB_USER'),
                      db_password=env('DB_PASSWORD'),
                      dp_port=env('DB_PORT')
                  )
                  )