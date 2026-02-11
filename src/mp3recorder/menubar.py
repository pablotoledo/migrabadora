"""Menu bar app for MP3 Recorder on macOS.

This module provides a macOS menu bar interface for audio recording,
using rumps for the UI and integrating with the existing AudioRecorder class.
"""

import logging
import threading
import time
from datetime import datetime
from pathlib import Path

import rumps

# Try to import AppKit for bringing app to front (may not be available in all envs)
try:
    from AppKit import NSApplication

    HAS_APPKIT = True
except ImportError:
    HAS_APPKIT = False

from mp3recorder import __version__
from mp3recorder.config import load as load_config
from mp3recorder.config import save as save_config
from mp3recorder.dependencies import (
    get_blackhole_install_instructions,
    get_blackhole_url,
    open_path,
    open_url,
)
from mp3recorder.devices import AudioDevice, get_default_device, list_audio_devices
from mp3recorder.logging_config import (
    get_log_directory,
    log_startup_info,
    setup_logging,
)
from mp3recorder.recorder import AudioRecorder
from mp3recorder.startup import (
    get_uninstall_summary,
    install_launch_agent,
    is_launch_agent_installed,
    uninstall_app,
    uninstall_launch_agent,
)

logger = logging.getLogger(__name__)

# Bitrate options
BITRATE_OPTIONS = [128, 192, 256, 320]


class MP3RecorderMenuBar(rumps.App):
    """macOS menu bar application for MP3 recording."""

    def __init__(self) -> None:
        """Initialize the menu bar app."""
        super().__init__("MIC", quit_button=None)

        # Load configuration
        self.config = load_config()
        logger.debug(
            f"Loaded config: bitrate={self.config.bitrate}, output={self.config.output_folder}"
        )

        # Recording state
        self.is_recording = False
        self.recorder: AudioRecorder | None = None
        self.recording_thread: threading.Thread | None = None
        self.start_time: float = 0
        self.should_stop = False

        # Recent recordings
        self.recent_recordings: list[Path] = []

        # Set up selected device from config or default
        self.selected_device: AudioDevice | None = None
        self._load_device_from_config()

        # Output folder from config
        self.output_folder: Path = Path(self.config.output_folder).expanduser()

        # Build menu
        self._build_menu()

        # Timer for updating recording status
        self.timer = rumps.Timer(self._update_timer, 1)

        # Set title with emoji
        self.title = "🎙️"

    def _load_device_from_config(self) -> None:
        """Load saved device from config or use default."""
        if self.config.default_device:
            # Try to find the saved device
            devices = list_audio_devices()
            for device in devices:
                if device.name == self.config.default_device:
                    self.selected_device = device
                    logger.debug(f"Restored device from config: {device.name}")
                    return

        # Fall back to default device
        self.selected_device = get_default_device()

    def _build_menu(self) -> None:
        """Build the menu bar menu."""
        # Get output folder display name (shorten if too long)
        folder_name = (
            self.output_folder.name
            if len(str(self.output_folder)) > 30
            else str(self.output_folder)
        )

        self.menu = [
            rumps.MenuItem("Start Recording", callback=self._toggle_recording),
            None,  # Separator
            self._create_device_menu(),
            self._create_quality_menu(),
            rumps.MenuItem(
                f"Output Folder: {folder_name}", callback=self._choose_folder
            ),
            None,  # Separator
            self._create_recent_recordings_menu(),
            None,  # Separator
            self._create_start_at_login_item(),
            self._create_setup_guide_menu(),
            None,  # Separator
            rumps.MenuItem(
                f"About MP3 Recorder v{__version__}", callback=self._show_about
            ),
            rumps.MenuItem("Uninstall MP3 Recorder...", callback=self._show_uninstall),
            rumps.MenuItem("Quit", callback=self._quit),
        ]

    def _create_device_menu(self) -> rumps.MenuItem:
        """Create the device selection submenu."""
        device_menu = rumps.MenuItem("Select Device")

        devices = list_audio_devices()
        for device in devices:
            item = rumps.MenuItem(
                device.name,
                callback=lambda sender, d=device: self._select_device(sender, d),
            )
            # Mark current device
            if self.selected_device and device.index == self.selected_device.index:
                item.state = 1
            device_menu.add(item)

        if not devices:
            device_menu.add(rumps.MenuItem("No devices found", callback=None))

        return device_menu

    def _create_quality_menu(self) -> rumps.MenuItem:
        """Create the audio quality submenu."""
        quality_menu = rumps.MenuItem("Audio Quality")

        for bitrate in BITRATE_OPTIONS:
            item = rumps.MenuItem(
                f"{bitrate}k",
                callback=lambda sender, b=bitrate: self._select_bitrate(sender, b),
            )
            # Mark current bitrate
            if bitrate == self.config.bitrate:
                item.state = 1
            quality_menu.add(item)

        return quality_menu

    def _create_recent_recordings_menu(self) -> rumps.MenuItem:
        """Create the recent recordings submenu."""
        recent_menu = rumps.MenuItem("Recent Recordings")

        if self.recent_recordings:
            for path in self.recent_recordings[-5:]:  # Show last 5
                item = rumps.MenuItem(
                    path.name,
                    callback=lambda _, p=path: self._open_recording(p),
                )
                recent_menu.add(item)
        else:
            recent_menu.add(rumps.MenuItem("No recent recordings", callback=None))

        return recent_menu

    def _create_setup_guide_menu(self) -> rumps.MenuItem:
        """Create the setup guide submenu."""
        setup_menu = rumps.MenuItem("Help")

        setup_menu.add(
            rumps.MenuItem("Setup BlackHole...", callback=self._show_blackhole_help)
        )
        setup_menu.add(None)  # Separator
        setup_menu.add(
            rumps.MenuItem("Open Logs Folder", callback=self._open_logs_folder)
        )

        return setup_menu

    def _create_start_at_login_item(self) -> rumps.MenuItem:
        """Create the Start at Login toggle item."""
        item = rumps.MenuItem("Start at Login", callback=self._toggle_start_at_login)
        item.state = 1 if is_launch_agent_installed() else 0
        return item

    def _select_device(self, sender: rumps.MenuItem, device: AudioDevice) -> None:
        """Handle device selection."""
        self.selected_device = device
        logger.info(f"Selected device: {device.name}")

        # Update config
        self.config.default_device = device.name
        save_config(self.config)

        # Update menu checkmarks (exclusive selection)
        # We access the menu item directly to ensure we get the right parent
        try:
            device_menu = self.menu["Select Device"]
            for item in device_menu.values():
                if hasattr(item, "state"):
                    item.state = 0
            sender.state = 1
        except Exception as e:
            logger.error(f"Error updating menu state: {e}")
            # Fallback attempts
            sender.state = 1

    def _select_bitrate(self, sender: rumps.MenuItem, bitrate: int) -> None:
        """Handle bitrate selection."""
        self.config.bitrate = bitrate
        save_config(self.config)
        logger.info(f"Selected bitrate: {bitrate}k")

        # Update menu checkmarks (exclusive selection)
        try:
            quality_menu = self.menu["Audio Quality"]
            for item in quality_menu.values():
                if hasattr(item, "state"):
                    item.state = 0
            sender.state = 1
        except Exception as e:
            logger.error(f"Error updating quality menu state: {e}")
            sender.state = 1

    def _toggle_start_at_login(self, sender: rumps.MenuItem) -> None:
        """Toggle the Start at Login setting."""
        if is_launch_agent_installed():
            # Uninstall
            if uninstall_launch_agent():
                sender.state = 0
                self.config.start_at_login = False
                save_config(self.config)
                logger.info("Disabled Start at Login")
            else:
                rumps.alert("Error", "Could not disable Start at Login.")
        else:
            # Install
            if install_launch_agent():
                sender.state = 1
                self.config.start_at_login = True
                save_config(self.config)
                logger.info("Enabled Start at Login")
            else:
                rumps.alert("Error", "Could not enable Start at Login.")

    def _toggle_recording(self, _sender: rumps.MenuItem) -> None:
        """Toggle recording on/off."""
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        """Start indefinite audio recording."""
        if self.selected_device is None:
            rumps.alert(
                title="No Device Selected",
                message="Please select an audio input device first.",
            )
            return

        try:
            if self.selected_device:
                logger.debug(f"Selected device: {self.selected_device}")

                # SMART SWITCH: If Multi-Output (0 inputs) is selected, try to find BlackHole automatically.
                # The user wants to record the output, which means they should be listening on the BlackHole input.
                if self.selected_device.channels < 1:
                    logger.info("Attempting smart switch for Multi-Output device")
                    devices = list_audio_devices()
                    blackhole = next(
                        (d for d in devices if "BlackHole" in d.name), None
                    )

                    if blackhole:
                        logger.info(
                            f"Switching from '{self.selected_device.name}' to '{blackhole.name}'"
                        )
                        # Notify user non-intrusively
                        rumps.notification(
                            title="Audio Routing Auto-Switch",
                            subtitle=f"Using {blackhole.name}",
                            message="Multi-Output sends audio. BlackHole receives it. Recording from BlackHole.",
                        )
                        # Update selection
                        self.selected_device = blackhole
                        # Update config persistent
                        self.config.default_device = blackhole.name
                        save_config(self.config)
                        # Update visual menu state
                        try:
                            device_menu = self.menu["Select Device"]
                            for item in device_menu.values():
                                if hasattr(item, "state"):
                                    item.state = 0
                                if item.title == blackhole.name:
                                    item.state = 1
                        except Exception as exc:
                            logger.warning(f"Could not update menu visuals: {exc}")

            # Create recorder with selected device and config settings
            channels = self.selected_device.channels if self.selected_device else 2
            sample_rate = (
                int(self.selected_device.sample_rate) if self.selected_device else 44100
            )

            self.recorder = AudioRecorder(
                device=self.selected_device.index if self.selected_device else None,
                channels=channels,
                sample_rate=sample_rate,
                bitrate=f"{self.config.bitrate}k",
            )

            try:
                # Start recording (non-blocking)
                self.recorder.start()
                self.is_recording = True
                self.start_time = time.time()

                # Update menu
                self.menu["Start Recording"].title = "Stop Recording"
                self.timer.start()

                logger.info("Recording started")

            except Exception as e:
                logger.error(f"Failed to start recording: {e}")
                rumps.alert(
                    title="Recording Error",
                    message=f"Could not start recording from '{self.selected_device.name}'.\n\n"
                    f"Error: {e!s}\n\n"
                    "Note: Multi-Output devices are typically output-only. "
                    "Try using BlackHole for system audio recording.",
                )
                self.recorder = None
                return
            self.menu["Start Recording"].title = "Stop Recording"
            self.title = "🔴"

            # Start timer to update display
            self.timer.start()

            logger.info("Recording started")

        except Exception as e:
            logger.error(f"Recording error: {e}")
            self._on_recording_error(str(e))

    def _stop_recording(self) -> None:
        """Stop the current recording."""
        self.is_recording = False
        self.timer.stop()

        # Disable button while saving
        self.menu["Start Recording"].title = "Saving..."
        self.menu["Start Recording"].set_callback(None)

        # Finish in background thread
        threading.Thread(target=self._finish_recording).start()

    def _finish_recording(self) -> None:
        """Stop recorder and save file (runs in background thread)."""
        try:
            if self.recorder:
                self.recorder.stop()
                self._save_recording()
        except Exception as e:
            logger.error(f"Finish recording error: {e}")
            self._on_recording_error(str(e))
        finally:
            self._on_recording_complete()

    def _safe_notification(self, title: str, subtitle: str, message: str) -> None:
        """Safely show notification, falling back to alert on error."""
        try:
            rumps.notification(
                title=title,
                subtitle=subtitle,
                message=message,
                sound=True,
            )
        except Exception as e:
            logger.warning(f"Notification failed: {e}")
            if "Info.plist" in str(e) or "CFBundleIdentifier" in str(e):
                logger.info("Using alert fallback for notification")
                rumps.alert(title, f"{subtitle}\n{message}")

    def _save_recording(self) -> None:
        """Save the recorded audio as MP3."""
        if self.recorder is None:
            return

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"recording_{timestamp}.mp3"
        output_path = self.output_folder / filename

        duration = int(time.time() - self.start_time)
        duration_str = f"{duration // 60}:{duration % 60:02d}"

        try:
            saved_path = self.recorder.save_mp3(output_path)

            # Add to recent recordings
            self.recent_recordings.append(saved_path)
            if len(self.recent_recordings) > 5:
                self.recent_recordings = self.recent_recordings[-5:]

            # Rebuild menu to update recent recordings
            self._build_menu()

            # Show notification with filename and duration
            self._safe_notification(
                title="Recording Complete",
                subtitle=f"Duration: {duration_str}",
                message=filename,
            )

            logger.info(f"Saved recording: {saved_path} ({duration_str})")

        except Exception as e:
            self._on_recording_error(f"Failed to save: {e}")

    def _on_recording_complete(self) -> None:
        """Handle recording completion."""
        self.is_recording = False
        self.recorder = None

        # Update menu
        self.menu["Start Recording"].title = "Start Recording"
        self.menu["Start Recording"].set_callback(self._toggle_recording)
        self.title = "🎙️"

    def _on_recording_error(self, error_message: str) -> None:
        """Handle recording error."""
        self._safe_notification(
            title="Recording Error",
            subtitle="An error occurred",
            message=error_message,
        )
        self._on_recording_complete()

    def _update_timer(self, _: rumps.Timer) -> None:
        """Update the timer display during recording."""
        if not self.is_recording:
            return

        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60

        # Update menu bar title with MM:SS format
        self.title = f"🔴 {minutes}:{seconds:02d}"

    def _choose_folder(self, _: rumps.MenuItem) -> None:
        """Open dialog to choose output folder."""
        response = rumps.Window(
            title="Choose Output Folder",
            message=f"Current folder: {self.output_folder}\n\nEnter new folder path:",
            default_text=str(self.output_folder),
            ok="Save",
            cancel="Cancel",
            dimensions=(400, 24),
        ).run()

        if response.clicked:
            new_path = Path(response.text.strip()).expanduser()
            if new_path.is_dir():
                self.output_folder = new_path
                self._update_folder_config(new_path)
            elif not new_path.exists():
                try:
                    new_path.mkdir(parents=True)
                    self.output_folder = new_path
                    self._update_folder_config(new_path)
                except OSError as e:
                    rumps.alert("Invalid Folder", f"Could not create folder: {e}")
            else:
                rumps.alert("Invalid Folder", "Please enter a valid directory path.")

    def _update_folder_config(self, new_path: Path) -> None:
        """Update folder in config and rebuild menu."""
        self.config.output_folder = str(new_path)
        save_config(self.config)
        self._build_menu()
        logger.info(f"Updated output folder: {new_path}")

    def _open_recording(self, path: Path) -> None:
        """Open a recording in Finder."""
        if path.exists():
            open_path(path.parent)
        else:
            rumps.alert("File Not Found", f"Recording not found:\n{path}")

    def _show_blackhole_help(self, _: rumps.MenuItem) -> None:
        """Show BlackHole setup instructions."""
        instructions = get_blackhole_install_instructions()
        url = get_blackhole_url()

        response = rumps.alert(
            title="Setup BlackHole",
            message=instructions[:500]
            + "...\n\n(Full instructions on website)",  # Truncate for alert
            ok="Open Website",
            cancel="Close",
        )

        if response == 1:  # OK button clicked
            open_url(url)

    def _open_logs_folder(self, _: rumps.MenuItem) -> None:
        """Open the logs folder in Finder."""
        log_dir = get_log_directory()
        if log_dir.exists():
            open_path(log_dir)
        else:
            rumps.alert("Logs Folder", f"Logs folder not found:\n{log_dir}")

    def _bring_to_front(self) -> None:
        """Bring the app to the foreground for dialogs."""
        if HAS_APPKIT:
            try:
                NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
            except Exception as e:
                logger.debug(f"Could not bring app to front: {e}")

    def _show_about(self, _: rumps.MenuItem) -> None:
        """Show about dialog."""
        self._bring_to_front()
        try:
            from mp3recorder.dependencies import get_system_info

            info = get_system_info()

            message = f"""MP3 Recorder v{__version__}

A simple menu bar app for recording audio on macOS.

FFmpeg: {'✓ Found' if info['ffmpeg_available'] else '✗ Not Found'}
BlackHole: {'✓ Found' if info['blackhole_available'] else '✗ Not Found'}

Python: {info['python_version'].split()[0]}
macOS: {info['macos_version']}
"""
        except Exception as e:
            logger.error(f"Error getting system info for About dialog: {e}")
            message = f"""MP3 Recorder v{__version__}

A simple menu bar app for recording audio on macOS.
"""

        rumps.alert(title="About MP3 Recorder", message=message)

    def _show_uninstall(self, _: rumps.MenuItem) -> None:
        """Show uninstall confirmation dialog."""
        self._bring_to_front()
        summary = get_uninstall_summary()

        response = rumps.alert(
            title="Uninstall MP3 Recorder",
            message=f"{summary}\n\nThis will NOT remove the application itself.\n\nAre you sure?",
            ok="Uninstall",
            cancel="Cancel",
        )

        if response == 1:  # OK button clicked
            results = uninstall_app(remove_config=True, remove_logs=True)

            if all(results.values()):
                rumps.alert(
                    "Uninstall Complete",
                    "All MP3 Recorder data has been removed.\n\n"
                    "You can now move the application to Trash.",
                )
                rumps.quit_application()
            else:
                failed = [k for k, v in results.items() if not v]
                rumps.alert(
                    "Uninstall Warning",
                    f"Some items could not be removed: {', '.join(failed)}\n\n"
                    "You may need to remove them manually.",
                )

    def _quit(self, _: rumps.MenuItem) -> None:
        """Quit the application."""
        if self.is_recording:
            self.should_stop = True
            if self.recording_thread:
                self.recording_thread.join(timeout=2)

        logger.info("Application quitting")
        rumps.quit_application()


def main() -> None:
    """Main entry point for the menu bar app."""
    # Load config first to get debug mode
    config = load_config()

    # Setup logging
    setup_logging(debug=config.debug_mode)
    log_startup_info()

    logger.info("Starting MP3 Recorder Menu Bar...")
    logger.debug("Creating app instance...")
    app = MP3RecorderMenuBar()
    logger.debug(f"App title: {app.title}")
    logger.debug(f"App menu items: {list(app.menu.keys()) if app.menu else 'None'}")
    logger.info("Running app - icon should appear in menu bar now...")
    app.run()


if __name__ == "__main__":
    main()
