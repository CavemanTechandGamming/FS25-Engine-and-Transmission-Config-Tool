"""Lightweight rotating file logger (stays small; useful for bug reports)."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from src.core.paths import get_app_dir, log_path

_configured = False


def setup_logging() -> logging.Logger:
    """
    Configure the app logger once.
    Rotating file: ~256 KiB x 2 backups so it cannot bloat the portable folder.
    """
    global _configured
    logger = logging.getLogger("fs25config")
    if _configured:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    get_app_dir().mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        log_path(),
        maxBytes=256 * 1024,
        backupCount=2,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)

    # Keep console quiet unless something goes wrong at import time
    _configured = True
    logger.info("Logging started (file=%s)", log_path())
    return logger
