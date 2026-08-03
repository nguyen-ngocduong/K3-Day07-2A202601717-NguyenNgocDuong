"""
src/log.py — Centralized Logger Configuration for RAG System.

Configures logging to output to both console and logs/app.log file.
"""

from __future__ import annotations

import logging
from pathlib import Path

# Path to log file
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"


def get_logger(name: str = "rag_app") -> logging.Logger:
    """
    Get or create a logger with dual handlers (stream console + file app.log).

    Args:
        name: Name of the logger instance.

    Returns:
        logging.Logger configured.
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if already configured
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    return logger