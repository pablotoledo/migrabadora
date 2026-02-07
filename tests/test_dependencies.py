"""Unit tests for the dependencies module."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mp3recorder.dependencies import (
    check_blackhole,
    check_ffmpeg,
    copy_to_clipboard,
    get_blackhole_install_instructions,
    get_blackhole_url,
    get_bundled_ffmpeg,
    get_ffmpeg_clipboard_command,
    get_ffmpeg_install_instructions,
    get_ffmpeg_path,
    get_ffmpeg_version,
    get_system_info,
    open_path,
    open_url,
)
import mp3recorder.dependencies as deps_module


class TestCheckFfmpeg:
    """Tests for check_ffmpeg function."""

    def setup_method(self):
        """Reset the FFmpeg path cache before each test."""
        deps_module._ffmpeg_path_cache = None

    def test_returns_true_when_bundled_found(self):
        """Should return True when bundled FFmpeg is found."""
        with patch("mp3recorder.dependencies.get_bundled_ffmpeg") as mock_bundled:
            mock_bundled.return_value = "/path/to/bundled/ffmpeg"

            available, path = check_ffmpeg()

            assert available is True
            assert "ffmpeg" in path

    def test_returns_true_when_system_found(self):
        """Should return True when system FFmpeg is found (no bundled)."""
        with patch("mp3recorder.dependencies.get_bundled_ffmpeg") as mock_bundled, \
             patch("shutil.which") as mock_which:
            mock_bundled.return_value = None
            mock_which.return_value = "/usr/local/bin/ffmpeg"

            deps_module._ffmpeg_path_cache = None  # Reset cache
            available, path = check_ffmpeg()

            assert available is True
            assert path == "/usr/local/bin/ffmpeg"

    def test_returns_false_when_not_found(self):
        """Should return False and None when FFmpeg is not found."""
        with patch("mp3recorder.dependencies.get_bundled_ffmpeg") as mock_bundled, \
             patch("shutil.which") as mock_which:
            mock_bundled.return_value = None
            mock_which.return_value = None

            deps_module._ffmpeg_path_cache = None  # Reset cache
            available, path = check_ffmpeg()

            assert available is False
            assert path is None


class TestCheckBlackhole:
    """Tests for check_blackhole function."""

    def test_returns_true_when_found(self):
        """Should return True and device name when BlackHole is found."""
        mock_devices = [
            {"name": "Built-in Microphone", "max_input_channels": 1},
            {"name": "BlackHole 2ch", "max_input_channels": 2},
        ]

        with patch("sounddevice.query_devices") as mock_query:
            mock_query.return_value = mock_devices

            available, name = check_blackhole()

            assert available is True
            assert name == "BlackHole 2ch"

    def test_returns_false_when_not_found(self):
        """Should return False when BlackHole is not found."""
        mock_devices = [
            {"name": "Built-in Microphone", "max_input_channels": 1},
            {"name": "USB Audio Device", "max_input_channels": 2},
        ]

        with patch("sounddevice.query_devices") as mock_query:
            mock_query.return_value = mock_devices

            available, name = check_blackhole()

            assert available is False
            assert name is None

    def test_handles_exception(self):
        """Should handle exceptions gracefully."""
        with patch("sounddevice.query_devices") as mock_query:
            mock_query.side_effect = RuntimeError("Device error")

            available, name = check_blackhole()

            assert available is False
            assert name is None


class TestGetFfmpegVersion:
    """Tests for get_ffmpeg_version function."""

    def test_returns_version_string(self):
        """Should return version string when FFmpeg is available."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="ffmpeg version 6.0 Copyright (c) 2000-2023\nbuilt with...",
            )

            version = get_ffmpeg_version()

            assert "ffmpeg version 6.0" in version

    def test_returns_none_on_error(self):
        """Should return None when FFmpeg is not available."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            version = get_ffmpeg_version()

            assert version is None


class TestGetSystemInfo:
    """Tests for get_system_info function."""

    def setup_method(self):
        """Reset cache before each test."""
        deps_module._ffmpeg_path_cache = None

    def test_returns_dict_with_expected_keys(self):
        """Should return dict with all expected keys."""
        with patch("mp3recorder.dependencies.get_bundled_ffmpeg") as mock_bundled, \
             patch("shutil.which") as mock_which, \
             patch("sounddevice.query_devices") as mock_query:
            mock_bundled.return_value = None
            mock_which.return_value = "/usr/local/bin/ffmpeg"
            mock_query.return_value = []

            info = get_system_info()

            assert "app_version" in info
            assert "python_version" in info
            assert "macos_version" in info
            assert "ffmpeg_available" in info
            assert "ffmpeg_path" in info
            assert "blackhole_available" in info


class TestInstructions:
    """Tests for installation instruction functions."""

    def test_ffmpeg_instructions_not_empty(self):
        """Should return non-empty FFmpeg instructions."""
        instructions = get_ffmpeg_install_instructions()

        assert len(instructions) > 100
        assert "FFmpeg" in instructions
        assert "brew" in instructions.lower()

    def test_blackhole_instructions_not_empty(self):
        """Should return non-empty BlackHole instructions."""
        instructions = get_blackhole_install_instructions()

        assert len(instructions) > 100
        assert "BlackHole" in instructions

    def test_ffmpeg_clipboard_command(self):
        """Should return brew install command."""
        command = get_ffmpeg_clipboard_command()

        assert command == "brew install ffmpeg"

    def test_blackhole_url(self):
        """Should return BlackHole website URL."""
        url = get_blackhole_url()

        assert "existential.audio" in url


class TestCopyToClipboard:
    """Tests for copy_to_clipboard function."""

    def test_copies_text(self):
        """Should copy text to clipboard using pbcopy."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock()

            result = copy_to_clipboard("test text")

            assert result is True
            mock_run.assert_called_once()
            assert mock_run.call_args[1]["input"] == b"test text"

    def test_returns_false_on_error(self):
        """Should return False on error."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            result = copy_to_clipboard("test text")

            assert result is False


class TestOpenUrl:
    """Tests for open_url function."""

    def test_opens_url(self):
        """Should open URL using open command."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock()

            result = open_url("https://example.com")

            assert result is True
            mock_run.assert_called_once_with(["open", "https://example.com"], check=True)

    def test_returns_false_on_error(self):
        """Should return False on error."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "open")

            result = open_url("https://example.com")

            assert result is False


class TestOpenPath:
    """Tests for open_path function."""

    def test_opens_path(self):
        """Should open path using open command."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock()

            result = open_path(Path("/tmp/test"))

            assert result is True
            mock_run.assert_called_once_with(["open", "/tmp/test"], check=True)

    def test_returns_false_on_error(self):
        """Should return False on error."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            result = open_path("/nonexistent")

            assert result is False
