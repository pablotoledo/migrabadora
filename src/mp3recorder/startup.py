"""Auto-startup management for MP3 Recorder using macOS LaunchAgents.

This module provides functions to manage automatic startup of the menu bar app
at login using macOS LaunchAgents.
"""

import logging
import plistlib
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# LaunchAgent configuration
LAUNCH_AGENT_LABEL = "com.mp3recorder.menubar"
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
LAUNCH_AGENT_PATH = LAUNCH_AGENTS_DIR / f"{LAUNCH_AGENT_LABEL}.plist"


def get_launch_agent_path() -> Path:
    """Get the path to the LaunchAgent plist file.

    Returns:
        Path to the plist file.
    """
    return LAUNCH_AGENT_PATH


def is_launch_agent_installed() -> bool:
    """Check if the LaunchAgent is installed.

    Returns:
        True if the plist file exists, False otherwise.
    """
    return LAUNCH_AGENT_PATH.exists()


def install_launch_agent(app_path: str | Path | None = None) -> bool:
    """Install a LaunchAgent to start the app at login.

    Args:
        app_path: Path to the .app bundle or the executable.
                  If None, uses the poetry script path.

    Returns:
        True if installation was successful, False otherwise.
    """
    # Determine the executable path
    if app_path:
        app_path = Path(app_path)
        if app_path.suffix == ".app":
            # It's an app bundle, point to the executable inside
            executable = app_path / "Contents" / "MacOS" / "mp3recorder-menubar"
            if not executable.exists():
                # Try alternative name
                executable = app_path / "Contents" / "MacOS" / "menubar"
        else:
            executable = app_path
    else:
        # Use the poetry script (for development)
        # This gets the path to the mp3recorder-menubar script
        import shutil

        script_path = shutil.which("mp3recorder-menubar")
        if script_path:
            executable = Path(script_path)
        else:
            # Fallback to python -m
            import sys

            executable = Path(sys.executable)
            logger.warning(
                "Could not find mp3recorder-menubar script, using Python executable"
            )

    plist_content = {
        "Label": LAUNCH_AGENT_LABEL,
        "ProgramArguments": [str(executable)],
        "RunAtLoad": True,
        "KeepAlive": False,
    }

    try:
        # Create LaunchAgents directory if it doesn't exist
        LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)

        # Write the plist file
        with LAUNCH_AGENT_PATH.open("wb") as f:
            plistlib.dump(plist_content, f)

        logger.info("Installed LaunchAgent at: %s", LAUNCH_AGENT_PATH)
        logger.debug("Executable path: %s", executable)

        # Load the agent (optional, it will load on next login anyway)
        try:
            subprocess.run(
                ["launchctl", "load", str(LAUNCH_AGENT_PATH)],
                check=True,
                capture_output=True,
            )
            logger.debug("LaunchAgent loaded successfully")
        except subprocess.CalledProcessError as e:
            # Not critical - will load on next login
            logger.debug("Could not load LaunchAgent immediately: %s", e)

        return True

    except (OSError, PermissionError) as e:
        logger.error("Failed to install LaunchAgent: %s", e)
        return False


def uninstall_launch_agent() -> bool:
    """Uninstall the LaunchAgent.

    Returns:
        True if uninstallation was successful, False otherwise.
    """
    if not LAUNCH_AGENT_PATH.exists():
        logger.info("LaunchAgent not installed, nothing to uninstall")
        return True

    try:
        # Unload the agent first
        try:
            subprocess.run(
                ["launchctl", "unload", str(LAUNCH_AGENT_PATH)],
                check=True,
                capture_output=True,
            )
            logger.debug("LaunchAgent unloaded successfully")
        except subprocess.CalledProcessError as e:
            # Not critical - might not be loaded
            logger.debug("Could not unload LaunchAgent: %s", e)

        # Remove the plist file
        LAUNCH_AGENT_PATH.unlink()
        logger.info("Uninstalled LaunchAgent: %s", LAUNCH_AGENT_PATH)

        return True

    except (OSError, PermissionError) as e:
        logger.error("Failed to uninstall LaunchAgent: %s", e)
        return False


def get_launch_agent_executable() -> str | None:
    """Get the executable path from an installed LaunchAgent.

    Returns:
        The executable path if installed, None otherwise.
    """
    if not LAUNCH_AGENT_PATH.exists():
        return None

    try:
        with LAUNCH_AGENT_PATH.open("rb") as f:
            plist = plistlib.load(f)

        args = plist.get("ProgramArguments", [])
        if args:
            return args[0]
        return None

    except (OSError, plistlib.InvalidFileException) as e:
        logger.error("Failed to read LaunchAgent: %s", e)
        return None


def uninstall_app(
    remove_config: bool = True, remove_logs: bool = True
) -> dict[str, bool]:
    """Completely uninstall the MP3 Recorder application data.

    This removes:
    - LaunchAgent (auto-start at login)
    - Configuration files (if remove_config is True)
    - Log files (if remove_logs is True)

    Note: This does NOT remove the application bundle itself.

    Args:
        remove_config: Whether to remove config files.
        remove_logs: Whether to remove log files.

    Returns:
        Dictionary with success status for each component.
    """
    from mp3recorder.config import CONFIG_DIR
    from mp3recorder.logging_config import LOG_DIR

    results = {
        "launch_agent": False,
        "config": False,
        "logs": False,
    }

    # Remove LaunchAgent
    results["launch_agent"] = uninstall_launch_agent()

    # Remove config directory
    if remove_config:
        try:
            if CONFIG_DIR.exists():
                import shutil

                shutil.rmtree(CONFIG_DIR)
                logger.info("Removed config directory: %s", CONFIG_DIR)
            results["config"] = True
        except (OSError, PermissionError) as e:
            logger.error("Failed to remove config directory: %s", e)
            results["config"] = False
    else:
        results["config"] = True

    # Remove logs directory
    if remove_logs:
        try:
            if LOG_DIR.exists():
                import shutil

                shutil.rmtree(LOG_DIR)
                logger.info("Removed logs directory: %s", LOG_DIR)
            results["logs"] = True
        except (OSError, PermissionError) as e:
            logger.error("Failed to remove logs directory: %s", e)
            results["logs"] = False
    else:
        results["logs"] = True

    return results


def get_uninstall_summary() -> str:
    """Get a summary of what will be removed during uninstall.

    Returns:
        Multi-line string describing what will be removed.
    """
    from mp3recorder.config import CONFIG_DIR
    from mp3recorder.logging_config import LOG_DIR

    items = []

    if LAUNCH_AGENT_PATH.exists():
        items.append(f"• LaunchAgent: {LAUNCH_AGENT_PATH}")

    if CONFIG_DIR.exists():
        items.append(f"• Configuration: {CONFIG_DIR}")

    if LOG_DIR.exists():
        items.append(f"• Logs: {LOG_DIR}")

    if items:
        return "The following will be removed:\n\n" + "\n".join(items)
    else:
        return "No MP3 Recorder data found to remove."
