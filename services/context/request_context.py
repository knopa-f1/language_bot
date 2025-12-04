class RequestContext:
    def __init__(self, session, i18n=None, lang: str | None = None):
        self.session = session
        self.i18n = i18n
        self.lang = lang
