import pytest
from unittest.mock import Mock

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config_data.constants import DefaultSettings
from services.context.global_context import GlobalContext
from services.context.request_context import RequestContext
from db import Base
from db.repositories.chats import ChatsRepository
from db.repositories.statistics import StatisticsRepository
from db.repositories.users import UsersRepository
from db.repositories.words import WordsRepository
from utils.i18n import create_translator_hub


@pytest.fixture
def cache():
    return Mock()


@pytest.fixture
def global_context(cache):
    hub = create_translator_hub()
    lang = "ru"
    i18n = hub.get_translator_by_locale(locale=lang)
    return GlobalContext(
        config=None, cache=cache, translator_hub=hub, default_settings=DefaultSettings(), session_pool=None
    )


@pytest.fixture
def request_context(global_context, session):
    lang = "ru"
    i18n = global_context.translator_hub.get_translator_by_locale(locale=lang)
    return RequestContext(session=session, i18n=i18n, lang=lang)


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
