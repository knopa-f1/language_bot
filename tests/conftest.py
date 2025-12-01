import pytest
from unittest.mock import Mock

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config_data.constants import DefaultSettings
from db import Base
from db.repositories.chats import ChatsRepository
from db.repositories.statistics import StatisticsRepository
from db.repositories.users import UsersRepository
from db.repositories.words import WordsRepository
from services.base_service import Context
from utils.i18n import create_translator_hub


@pytest.fixture
def cache():
    return Mock()


@pytest.fixture
def context(cache):
    hub = create_translator_hub()
    lang = "ru"
    i18n = hub.get_translator_by_locale(locale=lang)
    return Context(
        session="dummy_session",
        cache=cache,
        i18n=i18n,
        default_settings=DefaultSettings(),
        lang=lang,
    )


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine):
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        yield session


@pytest.fixture(autouse=True)
async def clean_db(session):
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())
    await session.commit()


@pytest.fixture
def words_repo(session):
    return WordsRepository(session)


@pytest.fixture
def stats_repo(session):
    return StatisticsRepository(session)


@pytest.fixture
def chats_repo(session):
    return ChatsRepository(session)


@pytest.fixture
def users_repo(session):
    return UsersRepository(session)
