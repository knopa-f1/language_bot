import asyncio
import datetime
import logging
import sys

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration

from cache.cache import create_cache
from config_data.config import ConfigSettings
from config_data.constants import DefaultSettings
from config_data.logging_config import setup_logging
from services.context.global_context import GlobalContext
from handlers import chat_status_handlers, other_handlers, user_handlers
from keyboards.set_menu import set_main_menu
from middlewares.chat_event import ChatEventsMiddleware
from middlewares.i18n import TranslatorRunnerMiddleware
from middlewares.session import DbSessionMiddleware
from middlewares.users import TrackAllUsersMiddleware
from services.schedule_tasks import job_send_messages_to_users
from services.service_factory import ServiceFactory
from utils.i18n import create_translator_hub


# start bot
async def main():
    # load config
    config = ConfigSettings()

    # --- Sentry ---
    sentry_dsn = config.sentry_dsn
    if sentry_dsn:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR,
        )
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[sentry_logging, AsyncioIntegration()],
            traces_sample_rate=0.0,
            environment=config.env_type,
        )

    # logging
    setup_logging(config.env_type, config.is_docker)
    logger = logging.getLogger(__name__)

    # db
    engine = create_async_engine(url=str(config.db.dsn), echo=True if config.env_type == "test" else False)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    translator_hub = create_translator_hub()
    scheduler = AsyncIOScheduler(timezone=datetime.timezone(datetime.timedelta(hours=+config.timezone)))

    # bot and dispatcher
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # workflow_data
    default_settings = DefaultSettings()
    cache = await create_cache(config)
    global_context = GlobalContext(
        config=config,
        session_pool=session_maker,
        cache=cache,
        default_settings=DefaultSettings(),
        translator_hub=translator_hub,
    )
    dp["global_context"] = global_context
    dp["service_factory"] = ServiceFactory(global_context)

    # set Menu
    await set_main_menu(bot, translator_hub.get_translator_by_locale(default_settings.chat_set.lang))

    # registration routers
    dp.include_router(user_handlers.router)
    dp.include_router(chat_status_handlers.router)
    dp.include_router(other_handlers.router)

    # registration middleware
    dp.update.outer_middleware(DbSessionMiddleware())
    dp.update.middleware(TranslatorRunnerMiddleware())
    dp.update.middleware(TrackAllUsersMiddleware())
    dp.update.middleware(ChatEventsMiddleware())

    # schedule reminders
    scheduler.add_job(
        job_send_messages_to_users,
        "cron",
        hour="*",
        args=(bot, translator_hub, session_maker, scheduler.timezone),
    )
    # scheduler.add_job(job_send_messages_to_users, 'cron', minute='*', args=(bot, translator_hub, session_maker, scheduler.timezone))
    scheduler.start()

    # start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, _translator_hub=translator_hub)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
