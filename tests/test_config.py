"""Unit tests for the config module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from mp3recorder.config import (
    CONFIG_VERSION,
    AppConfig,
    delete_config,
    get_config_directory,
    get_config_file,
    get_default_config,
    load,
    reset_to_defaults,
    save,
)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Use a temporary directory for config during tests."""
    import mp3recorder.config as cfg

    original_config_dir = cfg.CONFIG_DIR
    original_config_file = cfg.CONFIG_FILE

    # Override the module-level constants
    cfg.CONFIG_DIR = tmp_path
    cfg.CONFIG_FILE = tmp_path / "config.json"

    yield tmp_path

    # Restore original values
    cfg.CONFIG_DIR = original_config_dir
    cfg.CONFIG_FILE = original_config_file


class TestAppConfig:
    """Tests for AppConfig dataclass."""

    def test_default_values(self):
        """Should have sensible defaults."""
        config = AppConfig()

        assert "Desktop" in config.output_folder
        assert config.default_device is None
        assert config.sample_rate == 44100
        assert config.channels == 2
        assert config.bitrate == 192
        assert config.start_at_login is False
        assert config.debug_mode is False
        assert config.config_version == CONFIG_VERSION

    def test_custom_values(self):
        """Should accept custom values."""
        config = AppConfig(
            output_folder="/tmp/recordings",
            default_device="BlackHole 2ch",
            sample_rate=48000,
            channels=1,
            bitrate=320,
            start_at_login=True,
            debug_mode=True,
        )

        assert config.output_folder == "/tmp/recordings"
        assert config.default_device == "BlackHole 2ch"
        assert config.sample_rate == 48000
        assert config.channels == 1
        assert config.bitrate == 320
        assert config.start_at_login is True
        assert config.debug_mode is True

    def test_validates_bitrate(self):
        """Should reset invalid bitrate to default."""
        config = AppConfig(bitrate=999)

        assert config.bitrate == 192

    def test_validates_channels(self):
        """Should reset invalid channels to default."""
        config = AppConfig(channels=5)

        assert config.channels == 2

    def test_validates_sample_rate(self):
        """Should reset invalid sample rate to default."""
        config = AppConfig(sample_rate=12345)

        assert config.sample_rate == 44100

    def test_expands_user_path(self):
        """Should expand ~ in output folder path."""
        config = AppConfig(output_folder="~/test_folder")

        assert "~" not in config.output_folder
        assert Path.home().name in config.output_folder


class TestSaveLoad:
    """Tests for save and load functions."""

    def test_save_creates_directory(self, temp_config_dir):
        """Should create config directory if it doesn't exist."""
        config_subdir = temp_config_dir / "subdir"
        import mp3recorder.config as cfg

        cfg.CONFIG_DIR = config_subdir
        cfg.CONFIG_FILE = config_subdir / "config.json"

        config = AppConfig()
        save(config)

        assert config_subdir.exists()

    def test_save_creates_json_file(self, temp_config_dir):
        """Should create a valid JSON file."""
        config = AppConfig(bitrate=256)
        save(config)

        import mp3recorder.config as cfg

        assert cfg.CONFIG_FILE.exists()

        with open(cfg.CONFIG_FILE) as f:
            data = json.load(f)
        assert data["bitrate"] == 256

    def test_load_returns_saved_config(self, temp_config_dir):
        """Should load previously saved config."""
        original = AppConfig(
            output_folder="/tmp/test",
            bitrate=320,
            start_at_login=True,
        )
        save(original)

        loaded = load()

        assert loaded.output_folder == "/tmp/test"
        assert loaded.bitrate == 320
        assert loaded.start_at_login is True

    def test_load_returns_defaults_when_file_missing(self, temp_config_dir):
        """Should return defaults when config file doesn't exist."""
        loaded = load()

        assert loaded == get_default_config()

    def test_load_handles_corrupted_json(self, temp_config_dir):
        """Should return defaults when config file is corrupted."""
        import mp3recorder.config as cfg

        # Write invalid JSON
        with open(cfg.CONFIG_FILE, "w") as f:
            f.write("{ invalid json }")

        loaded = load()

        assert loaded == get_default_config()

    def test_load_handles_invalid_values(self, temp_config_dir):
        """Should use defaults for invalid field values."""
        import mp3recorder.config as cfg

        # Write JSON with invalid type for a field
        with open(cfg.CONFIG_FILE, "w") as f:
            json.dump({"bitrate": "not_a_number"}, f)

        # This should fail during AppConfig construction
        loaded = load()

        # Should return defaults
        assert loaded.bitrate == 192

    def test_load_ignores_unknown_fields(self, temp_config_dir):
        """Should ignore unknown fields in config file."""
        import mp3recorder.config as cfg

        with open(cfg.CONFIG_FILE, "w") as f:
            json.dump({
                "bitrate": 256,
                "unknown_field": "should be ignored",
                "another_unknown": 123,
            }, f)

        loaded = load()

        assert loaded.bitrate == 256
        assert not hasattr(loaded, "unknown_field")


class TestResetToDefaults:
    """Tests for reset_to_defaults function."""

    def test_resets_and_saves(self, temp_config_dir):
        """Should reset config and save to disk."""
        # Save a custom config first
        save(AppConfig(bitrate=320, start_at_login=True))

        # Reset to defaults
        config = reset_to_defaults()

        assert config.bitrate == 192
        assert config.start_at_login is False

        # Verify it was saved
        loaded = load()
        assert loaded.bitrate == 192


class TestMigration:
    """Tests for config migration."""

    def test_migrates_old_config(self, temp_config_dir):
        """Should migrate config from older versions."""
        import mp3recorder.config as cfg

        # Write old config without version
        with open(cfg.CONFIG_FILE, "w") as f:
            json.dump({"bitrate": 256}, f)

        loaded = load()

        assert loaded.config_version == CONFIG_VERSION


class TestPathFunctions:
    """Tests for path helper functions."""

    def test_get_config_directory(self):
        """Should return config directory path."""
        config_dir = get_config_directory()

        assert isinstance(config_dir, Path)
        assert "MP3Recorder" in str(config_dir)

    def test_get_config_file(self):
        """Should return config file path."""
        config_file = get_config_file()

        assert isinstance(config_file, Path)
        assert config_file.name == "config.json"


class TestDeleteConfig:
    """Tests for delete_config function."""

    def test_deletes_config_file(self, temp_config_dir):
        """Should delete config file."""
        save(AppConfig())

        import mp3recorder.config as cfg

        assert cfg.CONFIG_FILE.exists()

        result = delete_config()

        assert result is True
        assert not cfg.CONFIG_FILE.exists()

    def test_returns_true_when_not_exists(self, temp_config_dir):
        """Should return True when file doesn't exist."""
        result = delete_config()

        assert result is True
