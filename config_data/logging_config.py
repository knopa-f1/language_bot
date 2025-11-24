import logging
import logging.config


def setup_logging(env_type: str) -> None:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "DEBUG" if env_type == "test" else "INFO",
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "logs/app.log",
                "formatter": "standard",
                "level": "DEBUG" if env_type == "test" else "INFO",
                "when": "midnight",
                "interval": 1,  # every day
                "backupCount": 30,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    }

    logging.config.dictConfig(logging_config)
