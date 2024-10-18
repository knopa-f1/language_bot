from enum import Enum

from fluent_compiler.bundle import FluentBundle

from fluentogram import FluentTranslator, TranslatorHub

class Language(Enum):
    "Поддерживаемые языки"
    ru = "Русский"
    en = "English"

def create_translator_hub() -> TranslatorHub:
    translator_hub = TranslatorHub(
        {
            "ru": ("ru", "en"),
            "en": ("en", "ru")
        },
        [
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    locale="ru-RU",
                    filenames=["locales/ru/LC_MESSAGES/txt.ftl",
                               "locales/ru/LC_MESSAGES/buttons.ftl",
                               "locales/ru/LC_MESSAGES/settings.ftl"
                               ])),
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    locale="en-US",
                    filenames=["locales/en/LC_MESSAGES/txt.ftl",
                               "locales/en/LC_MESSAGES/buttons.ftl",
                               "locales/en/LC_MESSAGES/settings.ftl"
                               ]))
        ],
    )
    return translator_hub