from services.context.global_context import GlobalContext
from services.context.request_context import RequestContext


class BaseService:
    def __init__(self, global_context: GlobalContext, request_context: RequestContext):
        self.global_context = global_context
        self.request_context = request_context

    @property
    def session(self):
        return self.request_context.session

    @session.setter
    def session(self, session):
        self.request_context.session = session

    @property
    def cache(self):
        return self.global_context.cache

    @cache.setter
    def cache(self, cache):
        self.global_context.cache = cache

    @property
    def i18n(self):
        return self.request_context.i18n

    @i18n.setter
    def i18n(self, i18n):
        self.request_context.i18n = i18n

    @property
    def lang(self):
        return self.request_context.lang

    @lang.setter
    def lang(self, lang):
        self.request_context.lang = lang

    @property
    def default_settings(self):
        return self.global_context.default_settings

    @default_settings.setter
    def default_settings(self, default_settings):
        self.global_context.default_settings = default_settings
