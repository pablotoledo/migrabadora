"""Configuration persistence for MP3 Recorder.

This module provides centralized configuration management with JSON persistence
for the MP3 Recorder application.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Application name and config paths
APP_NAME = "MP3Recorder"
CONFIG_DIR = Path.home() / "Library" / "Application Support" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"

# Current config version for migrations
CONFIG_VERSION = 1


@dataclass
class AppConfig:
    """Application configuration settings.

    Attributes:
        output_folder: Directory where recordings are saved.
        default_device: Name or index of the default audio device.
        sample_rate: Audio sample rate in Hz.
        channels: Number of audio channels (1=mono, 2=stereo).
        bitrate: MP3 bitrate in kbps.
        start_at_login: Whether to start the app at login.
        debug_mode: Whether to enable debug logging.
        config_version: Version of the config format for migrations.
    """

    output_folder: str = field(default_factory=lambda: str(Path.home() / "Desktop"))
    default_device: str | None = None
    sample_rate: int = 44100
    channels: int = 2
    bitrate: int = 192
    start_at_login: bool = False
    debug_mode: bool = False
    config_version: int = CONFIG_VERSION

    def __post_init__(self) -> None:
        """Validate and normalize config values after initialization."""
        # Ensure output_folder is a valid path
        self.output_folder = str(Path(self.output_folder).expanduser())

        # Validate bitrate
        valid_bitrates = [128, 192, 256, 320]
        if self.bitrate not in valid_bitrates:
            logger.warning("Invalid bitrate %s, defaulting to 192", self.bitrate)
            self.bitrate = 192

        # Validate channels
        if self.channels not in [1, 2]:
            logger.warning("Invalid channels %s, defaulting to 2", self.channels)
            self.channels = 2

        # Validate sample rate
        valid_sample_rates = [44100, 48000, 96000]
        if self.sample_rate not in valid_sample_rates:
            logger.warning(
                "Invalid sample rate %s, defaulting to 44100", self.sample_rate
            )
            self.sample_rate = 44100


def get_default_config() -> AppConfig:
    """Get a new AppConfig with default values.

    Returns:
        AppConfig with all default values.
    """
    return AppConfig()


def load() -> AppConfig:
    """Load configuration from disk.

    Returns:
        AppConfig loaded from file, or defaults if file doesn't exist or is corrupted.
    """
    if not CONFIG_FILE.exists():
        logger.info("Config file not found, using defaults")
        return get_default_config()

    try:
        with CONFIG_FILE.open(encoding="utf-8") as f:
            data = json.load(f)

        # Handle migration if needed
        data = _migrate_config(data)

        # Create config from loaded data, ignoring unknown keys
        known_keys = {f.name for f in AppConfig.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_keys}

        config = AppConfig(**filtered_data)
        logger.debug("Loaded config from %s", CONFIG_FILE)
        return config

    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.error("Failed to load config, using defaults: %s", e)
        return get_default_config()


def save(config: AppConfig) -> None:
    """Save configuration to disk.

    Args:
        config: The AppConfig to save.
    """
    # Ensure config directory exists
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(asdict(config), f, indent=2)
        logger.debug("Saved config to %s", CONFIG_FILE)
    except OSError as e:
        logger.error("Failed to save config: %s", e)
        raise


def reset_to_defaults() -> AppConfig:
    """Reset configuration to defaults and save.

    Returns:
        The new default AppConfig.
    """
    config = get_default_config()
    save(config)
    logger.info("Config reset to defaults")
    return config


def _migrate_config(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate configuration from older versions.

    Args:
        data: The config data dictionary.

    Returns:
        Migrated config data.
    """
    version = data.get("config_version", 0)

    if version < CONFIG_VERSION:
        logger.info("Migrating config from version %s to %s", version, CONFIG_VERSION)

        # Add migration logic here as needed for future versions
        # Example:
        # if version < 2:
        #     data["new_field"] = "default_value"

        data["config_version"] = CONFIG_VERSION

    return data


def get_config_directory() -> Path:
    """Get the configuration directory path.

    Returns:
        Path to the config directory.
    """
    return CONFIG_DIR


def get_config_file() -> Path:
    """Get the config file path.

    Returns:
        Path to the config file.
    """
    return CONFIG_FILE


def delete_config() -> bool:
    """Delete the config file and directory.

    Returns:
        True if deletion was successful or file didn't exist.
    """
    try:
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
            logger.info("Deleted config file: %s", CONFIG_FILE)

        if CONFIG_DIR.exists() and not any(CONFIG_DIR.iterdir()):
            CONFIG_DIR.rmdir()
            logger.info("Deleted config directory: %s", CONFIG_DIR)

        return True
    except OSError as e:
        logger.error("Failed to delete config: %s", e)
        return False
