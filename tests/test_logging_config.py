"""Unit tests for the logging_config module."""

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from mp3recorder.logging_config import (
    get_log_directory,
    get_log_file,
    get_logger,
    log_startup_info,
    setup_logging,
)


@pytest.fixture
def reset_logging():
    """Reset logging configuration after each test."""
    yield
    # Reset the module-level flag
    import mp3recorder.logging_config as lc

    lc._logging_configured = False
    # Clear handlers from the mp3recorder logger
    logger = logging.getLogger("mp3recorder")
    logger.handlers.clear()


@pytest.fixture
def temp_log_dir(tmp_path):
    """Use a temporary directory for logs during tests."""
    import mp3recorder.logging_config as lc

    original_log_dir = lc.LOG_DIR
    original_log_file = lc.LOG_FILE

    # Override the module-level constants
    lc.LOG_DIR = tmp_path
    lc.LOG_FILE = tmp_path / "mp3recorder.log"

    yield tmp_path

    # Restore original values
    lc.LOG_DIR = original_log_dir
    lc.LOG_FILE = original_log_file


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_creates_log_directory(self, temp_log_dir, reset_logging):
        """Should create log directory if it doesn't exist."""
        log_subdir = temp_log_dir / "subdir"
        import mp3recorder.logging_config as lc

        lc.LOG_DIR = log_subdir
        lc.LOG_FILE = log_subdir / "test.log"

        setup_logging()

        assert log_subdir.exists()

    def test_creates_file_handler(self, temp_log_dir, reset_logging):
        """Should create a rotating file handler."""
        setup_logging()

        logger = logging.getLogger("mp3recorder")
        file_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert len(file_handlers) == 1

    def test_debug_mode_adds_console_handler(self, temp_log_dir, reset_logging):
        """Should add console handler in debug mode."""
        setup_logging(debug=True)

        logger = logging.getLogger("mp3recorder")
        stream_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(stream_handlers) >= 1

    def test_non_debug_mode_no_console_handler(self, temp_log_dir, reset_logging):
        """Should not add console handler in non-debug mode."""
        setup_logging(debug=False)

        logger = logging.getLogger("mp3recorder")
        # StreamHandler that is NOT a RotatingFileHandler
        pure_stream_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.StreamHandler)
            and not isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert len(pure_stream_handlers) == 0

    def test_idempotent(self, temp_log_dir, reset_logging):
        """Should only configure logging once."""
        setup_logging()
        setup_logging()  # Second call should be no-op

        logger = logging.getLogger("mp3recorder")
        file_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert len(file_handlers) == 1


class TestGetLogger:
    """Tests for get_logger function."""

    def test_returns_logger(self, reset_logging):
        """Should return a logger instance."""
        logger = get_logger("mp3recorder.test")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "mp3recorder.test"

    def test_logger_hierarchy(self, temp_log_dir, reset_logging):
        """Child logger should inherit from mp3recorder logger."""
        setup_logging()
        parent_logger = logging.getLogger("mp3recorder")
        child_logger = get_logger("mp3recorder.submodule")

        assert child_logger.parent == parent_logger


class TestLogStartupInfo:
    """Tests for log_startup_info function."""

    def test_logs_startup_info(self, temp_log_dir, reset_logging):
        """Should log startup information."""
        setup_logging()
        log_startup_info()

        import mp3recorder.logging_config as lc

        # Check that log file was written
        assert lc.LOG_FILE.exists()
        content = lc.LOG_FILE.read_text()
        assert "MP3 Recorder starting up" in content

    def test_logs_ffmpeg_status(self, temp_log_dir, reset_logging):
        """Should log FFmpeg availability."""
        setup_logging()

        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/local/bin/ffmpeg"
            log_startup_info()

        import mp3recorder.logging_config as lc

        content = lc.LOG_FILE.read_text()
        assert "FFmpeg" in content

    def test_logs_ffmpeg_not_found(self, temp_log_dir, reset_logging):
        """Should warn when FFmpeg is not found."""
        setup_logging()

        with patch("mp3recorder.dependencies.get_ffmpeg_path") as mock_get_path:
            mock_get_path.return_value = None
            log_startup_info()

        import mp3recorder.logging_config as lc

        content = lc.LOG_FILE.read_text()
        assert "FFmpeg: NOT FOUND" in content


class TestPathFunctions:
    """Tests for path helper functions."""

    def test_get_log_directory(self):
        """Should return log directory path."""
        log_dir = get_log_directory()

        assert isinstance(log_dir, Path)
        assert "MP3Recorder" in str(log_dir)

    def test_get_log_file(self):
        """Should return log file path."""
        log_file = get_log_file()

        assert isinstance(log_file, Path)
        assert log_file.name == "mp3recorder.log"
