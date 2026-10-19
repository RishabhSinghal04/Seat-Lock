import logging
from logging import StreamHandler, basicConfig
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
from typing import Final, TextIO

_FILE_NAME: Final[str] = "app.log"
_FILE_DIR: Final[str] = str(Path(__file__).resolve().parent.parent.parent / "logs")
_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_BACKUP_COUNT: Final[int] = 10
_DEFAULT_NOISY_LOGGERS: Final[tuple[str, ...]] = (
    "watchfiles",
    "watchfiles.main",
    "granian",
    "granian.access",
    "aiosqlite",
    "sqlalchemy.engine",
    "sqlalchemy.engine.Engine",
    "sqlalchemy.pool",
    "sqlalchemy.dialects",
    "asyncpg",  # PostgreSQL
    "aiopg",  # another PostgreSQL driver
    "aiomysql",  # MySQL
)


def setup_logging(
    debug: bool = False,
    log_format: str = _FORMAT,
    noisy_loggers: tuple[str, ...] | None = None,
) -> None:
    _ensure_log_directory()
    log_level: int = logging.DEBUG if debug else logging.INFO
    log_handler: list[StreamHandler[TextIO] | TimedRotatingFileHandler] = (
        _setup_handler(log_format)
    )
    basicConfig(level=log_level, handlers=log_handler, force=True)
    _silence_noisy_loggers(
        noisy_loggers if noisy_loggers is not None else _DEFAULT_NOISY_LOGGERS
    )


def _ensure_log_directory() -> None:
    try:
        os.makedirs(_FILE_DIR, exist_ok=True)
    except OSError as e:
        raise SystemExit(f"error creating directory '{_FILE_DIR}' : {e}")


def _setup_handler(
    log_format: str,
) -> list[StreamHandler[TextIO] | TimedRotatingFileHandler]:
    try:
        file_handler = TimedRotatingFileHandler(
            filename=os.path.join(_FILE_DIR, _FILE_NAME),
            when="midnight",
            interval=1,
            backupCount=_BACKUP_COUNT,
        )
    except OSError as e:
        raise SystemExit(f"error creating log file in '{_FILE_DIR}': {e}")
    file_handler.setFormatter(logging.Formatter(log_format))
    console_handler: StreamHandler[TextIO] = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    return [file_handler, console_handler]


def _silence_noisy_loggers(noisy_loggers: tuple[str, ...]) -> None:
    for name in noisy_loggers:
        _logger: logging.Logger = logging.getLogger(name)
        _logger.setLevel(logging.WARNING)
        _logger.propagate = False
