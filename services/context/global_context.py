class GlobalContext:
    def __init__(self, config, default_settings, cache, session_pool, translator_hub):
        self.config = config
        self.default_settings = default_settings
        self.cache = cache
        self.session_pool = session_pool
        self.translator_hub = translator_hub
