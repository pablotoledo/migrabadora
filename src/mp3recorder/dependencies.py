"""Dependency checking utilities for MP3 Recorder.

This module provides functions to check for required and optional dependencies
like FFmpeg and BlackHole, and provides installation instructions.
"""

import logging
import platform
import shutil
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Cache for FFmpeg path
_ffmpeg_path_cache: str | None = None


def get_bundled_ffmpeg() -> str | None:
    """Get the path to the bundled FFmpeg from imageio-ffmpeg.

    Returns:
        Path to bundled FFmpeg if available, None otherwise.
    """
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_path and Path(ffmpeg_path).exists():
            logger.debug(f"Bundled FFmpeg found at: {ffmpeg_path}")
            return ffmpeg_path
    except (ImportError, Exception) as e:
        logger.debug(f"imageio-ffmpeg not available: {e}")
    return None


def get_ffmpeg_path() -> str | None:
    """Get the best available FFmpeg path.

    Checks in order:
    1. Bundled FFmpeg from imageio-ffmpeg
    2. System FFmpeg in PATH

    Returns:
        Path to FFmpeg if found, None otherwise.
    """
    global _ffmpeg_path_cache

    if _ffmpeg_path_cache is not None:
        return _ffmpeg_path_cache

    # Try bundled FFmpeg first
    bundled = get_bundled_ffmpeg()
    if bundled:
        _ffmpeg_path_cache = bundled
        return bundled

    # Fall back to system FFmpeg
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        _ffmpeg_path_cache = system_ffmpeg
        logger.debug(f"System FFmpeg found at: {system_ffmpeg}")
        return system_ffmpeg

    return None


def check_ffmpeg() -> tuple[bool, str | None]:
    """Check if FFmpeg is installed and available.

    Checks bundled FFmpeg first, then falls back to system FFmpeg.

    Returns:
        Tuple of (is_available, path_if_found).
    """
    ffmpeg_path = get_ffmpeg_path()

    if ffmpeg_path:
        return True, ffmpeg_path

    logger.warning("FFmpeg not found (neither bundled nor in PATH)")
    return False, None


def check_blackhole() -> tuple[bool, str | None]:
    """Check if BlackHole audio device is available.

    Returns:
        Tuple of (is_available, device_name_if_found).
    """
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        for device in devices:
            if "blackhole" in device["name"].lower():
                device_name = device["name"]
                logger.debug(f"BlackHole device found: {device_name}")
                return True, device_name

        logger.info("BlackHole device not found")
        return False, None

    except Exception as e:
        logger.error(f"Error checking for BlackHole: {e}")
        return False, None


def get_ffmpeg_version() -> str | None:
    """Get the installed FFmpeg version string.

    Returns:
        Version string if available, None otherwise.
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            # First line usually contains version info
            first_line = result.stdout.split("\n")[0]
            return first_line
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def get_system_info() -> dict:
    """Get system information for diagnostics.

    Returns:
        Dictionary with system information.
    """
    try:
        from mp3recorder import __version__
    except ImportError:
        __version__ = "unknown"

    ffmpeg_available, ffmpeg_path = check_ffmpeg()
    blackhole_available, blackhole_name = check_blackhole()

    return {
        "app_version": __version__,
        "python_version": sys.version,
        "macos_version": platform.mac_ver()[0],
        "ffmpeg_available": ffmpeg_available,
        "ffmpeg_path": ffmpeg_path,
        "ffmpeg_version": get_ffmpeg_version() if ffmpeg_available else None,
        "blackhole_available": blackhole_available,
        "blackhole_device": blackhole_name,
    }


def get_ffmpeg_install_instructions() -> str:
    """Get instructions for installing FFmpeg.

    Returns:
        Multi-line string with installation instructions.
    """
    return """📦 Installing FFmpeg

FFmpeg is required to encode audio to MP3 format.

Option 1: Using Homebrew (Recommended)
1. Install Homebrew if not already installed:
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. Install FFmpeg:
   brew install ffmpeg

Option 2: Direct Download
1. Visit: https://ffmpeg.org/download.html
2. Download the macOS build
3. Extract and add to your PATH

To verify installation, run in Terminal:
  ffmpeg -version
"""


def get_blackhole_install_instructions() -> str:
    """Get instructions for installing and configuring BlackHole.

    Returns:
        Multi-line string with installation instructions.
    """
    return """🎧 Setting up BlackHole for System Audio Recording

BlackHole is a virtual audio driver that lets you record system audio.

Step 1: Install BlackHole
1. Visit: https://existential.audio/blackhole/
2. Download BlackHole 2ch (recommended)
3. Run the installer

Step 2: Configure Multi-Output Device
1. Open Audio MIDI Setup (Applications → Utilities)
2. Click '+' button at bottom left → Create Multi-Output Device
3. Check both "BlackHole 2ch" and your regular output (e.g., "MacBook Pro Speakers")
4. Right-click the Multi-Output Device → "Use This Device For Sound Output"

Step 3: In MP3 Recorder
1. Select "BlackHole 2ch" as the input device
2. Now you can record system audio!

Note: You won't hear audio while using Multi-Output Device.
To hear audio again, right-click your regular speakers and select "Use This Device For Sound Output".
"""


def get_ffmpeg_clipboard_command() -> str:
    """Get the FFmpeg install command for clipboard.

    Returns:
        The brew install command.
    """
    return "brew install ffmpeg"


def get_blackhole_url() -> str:
    """Get the BlackHole download URL.

    Returns:
        The BlackHole website URL.
    """
    return "https://existential.audio/blackhole/"


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard using pbcopy.

    Args:
        text: Text to copy.

    Returns:
        True if successful, False otherwise.
    """
    try:
        subprocess.run(
            ["pbcopy"],
            input=text.encode("utf-8"),
            check=True,
        )
        logger.debug("Copied to clipboard")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
        logger.error(f"Failed to copy to clipboard: {e}")
        return False


def open_url(url: str) -> bool:
    """Open a URL in the default browser.

    Args:
        url: URL to open.

    Returns:
        True if successful, False otherwise.
    """
    try:
        subprocess.run(["open", url], check=True)
        logger.debug(f"Opened URL: {url}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
        logger.error(f"Failed to open URL: {e}")
        return False


def open_path(path: Path | str) -> bool:
    """Open a path in Finder.

    Args:
        path: Path to open.

    Returns:
        True if successful, False otherwise.
    """
    try:
        subprocess.run(["open", str(path)], check=True)
        logger.debug(f"Opened path: {path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
        logger.error(f"Failed to open path: {e}")
        return False
