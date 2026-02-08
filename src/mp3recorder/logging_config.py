"""Logging configuration for MP3 Recorder.

This module provides centralized logging setup with rotating file handlers
for the MP3 Recorder application.
"""

import logging
import platform
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Application name for logging
APP_NAME = "MP3Recorder"

# Log directory and file paths
LOG_DIR = Path.home() / "Library" / "Logs" / APP_NAME
LOG_FILE = LOG_DIR / "mp3recorder.log"

# Log format
LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Rotation settings
MAX_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3

# Track if logging has been set up
_logging_configured = False


def setup_logging(debug: bool = False) -> None:
    """Configure logging for the MP3 Recorder application.

    Sets up a rotating file handler that writes to ~/Library/Logs/MP3Recorder/
    and optionally a console handler for debug mode.

    Args:
        debug: If True, also log to stderr and set level to DEBUG.
    """
    global _logging_configured

    if _logging_configured:
        return

    # Create log directory if it doesn't exist
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Get the root logger for the mp3recorder package
    root_logger = logging.getLogger("mp3recorder")
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Remove any existing handlers
    root_logger.handlers.clear()

    # Create rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    root_logger.addHandler(file_handler)

    # Add console handler in debug mode
    if debug:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        root_logger.addHandler(console_handler)

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the specified module.

    Args:
        name: The module name (typically __name__).

    Returns:
        A configured logger instance.
    """
    return logging.getLogger(name)


def log_startup_info() -> None:
    """Log application startup information.

    Logs version info, Python version, macOS version, and FFmpeg path.
    """
    logger = get_logger("mp3recorder.startup")

    # Import here to avoid circular imports
    try:
        from mp3recorder import __version__
    except ImportError:
        __version__ = "unknown"

    logger.info("=" * 50)
    logger.info("MP3 Recorder starting up")
    logger.info(f"Version: {__version__}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"macOS: {platform.mac_ver()[0]}")

    # Check for FFmpeg
    from mp3recorder.dependencies import get_ffmpeg_path

    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path:
        logger.info(f"FFmpeg: {ffmpeg_path}")
    else:
        logger.warning("FFmpeg: NOT FOUND")

    logger.info("=" * 50)


def get_log_directory() -> Path:
    """Get the log directory path.

    Returns:
        Path to the log directory.
    """
    return LOG_DIR


def get_log_file() -> Path:
    """Get the main log file path.

    Returns:
        Path to the main log file.
    """
    return LOG_FILE
