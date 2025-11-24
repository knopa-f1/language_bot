from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from cache.cache import Cache
from config_data.constants import DefaultSettings


class Context:
    def __init__(
        self,
        session: AsyncSession,
        cache: Cache | None = None,
        i18n: TranslatorRunner | None = None,
        default_settings: DefaultSettings | None = None,
        lang: str = "",
    ):
        self.session = session
        self.cache = cache
        self.i18n = i18n
        self.default_settings = default_settings
        self.lang = lang


class BaseService:
    def __init__(self, context: Context):
        self.context = context

    @property
    def session(self):
        return self.context.session

    @session.setter
    def session(self, session):
        self.context.session = session

    @property
    def cache(self):
        return self.context.cache

    @cache.setter
    def cache(self, cache):
        self.context.cache = cache

    @property
    def i18n(self):
        return self.context.i18n

    @i18n.setter
    def i18n(self, i18n):
        self.context.i18n = i18n

    @property
    def lang(self):
        return self.context.lang

    @lang.setter
    def lang(self, lang):
        self.context.lang = lang

    @property
    def default_settings(self):
        return self.context.default_settings

    @default_settings.setter
    def default_settings(self, default_settings):
        self.context.default_settings = default_settings
