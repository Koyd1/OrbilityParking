import logging
from logging.handlers import RotatingFileHandler

from app.config import AppConfig


def init_logging(config: AppConfig) -> None:
    """
    Configure console + rotating file logging for the application.
    """
    config.prepare_directories()
    level = getattr(logging, str(config.log_level).upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    file_handler = RotatingFileHandler(
        config.log_dir / "app.log", maxBytes=1_000_000, backupCount=5
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

