import logging
import logging.config
from typing import Dict, Any


def setup_logging(env_type: str, is_docker: bool) -> None:
    handlers: Dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "DEBUG" if env_type == "test" else "INFO",
        }
    }

    # Only add file logging if NOT running inside Docker
    if not is_docker:
        handlers["file"] = {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logs/app.log",
            "formatter": "standard",
            "level": "DEBUG" if env_type == "test" else "INFO",
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
        }

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": handlers,
        "root": {
            "handlers": list(handlers.keys()),
            "level": "DEBUG" if env_type == "test" else "INFO",
        },
    }

    logging.config.dictConfig(logging_config)
