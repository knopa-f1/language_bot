import pytest
from unittest.mock import Mock

from config_data.constants import DefaultSettings
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
