import asyncio
import logging
import sys
import datetime

from aiogram import Bot, Dispatcher
from cache.cache import Cache
from config_data.constants import DefaultSettings

from config_data.logging_config import setup_logging

from keyboards.set_menu import set_main_menu
from config_data.config import Config, load_config
from handlers import other_handlers, user_handlers
from middlewares.session import DbSessionMiddleware
from middlewares.users import TrackAllUsersMiddleware
from servises.schedule_tasks import job_send_messages_to_users

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from fluentogram import TranslatorHub
from middlewares.i18n import TranslatorRunnerMiddleware

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from utils.i18n import create_translator_hub


# start bot
async def main():
    # load config
    config: Config = load_config()

    # logging
    setup_logging(config.env_type)
    logger = logging.getLogger(__name__)

    # db
    engine = create_async_engine(
        url=str(config.db.dsn),
        echo=False
        # echo=True if config.env_type == "test" else False
    )

    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    translator_hub: TranslatorHub = create_translator_hub()
    scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone=datetime.timezone(datetime.timedelta(hours=+2)))

    # bot and dispatcher
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # workflow_data
    default_settings = DefaultSettings()
    dp["default_settings"] = default_settings
    dp["cache"] = Cache()

    # set Menu
    await set_main_menu(bot, translator_hub.get_translator_by_locale(default_settings.chat_set.lang))

    # registration routers
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # registration middleware
    dp.update.outer_middleware(DbSessionMiddleware(session_maker))
    dp.update.middleware(TranslatorRunnerMiddleware())
    dp.update.middleware(TrackAllUsersMiddleware())

    # schedule reminders
    scheduler.add_job(job_send_messages_to_users, 'cron', hour='*', args=(bot, translator_hub, session_maker))
    # scheduler.add_job(job_send_messages_to_users, 'cron', minute='*', args=(bot,))
    scheduler.start()

    # start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=['message', 'callback_query'], _translator_hub=translator_hub)


if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
