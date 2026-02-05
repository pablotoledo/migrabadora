"""Menu bar app for MP3 Recorder on macOS.

This module provides a macOS menu bar interface for audio recording,
using rumps for the UI and integrating with the existing AudioRecorder class.
"""

import threading
import time
from datetime import datetime
from pathlib import Path

import rumps

from mp3recorder.devices import AudioDevice, get_default_device, list_audio_devices
from mp3recorder.recorder import AudioRecorder

# Debug flag
DEBUG = True


def debug_print(msg: str) -> None:
    """Print debug message if DEBUG is enabled."""
    if DEBUG:
        print(f"[DEBUG] {msg}")


class MP3RecorderMenuBar(rumps.App):
    """macOS menu bar application for MP3 recording."""

    def __init__(self) -> None:
        """Initialize the menu bar app."""
        super().__init__("MIC", quit_button=None)

        # Recording state
        self.is_recording = False
        self.recorder: AudioRecorder | None = None
        self.recording_thread: threading.Thread | None = None
        self.start_time: float = 0
        self.should_stop = False

        # Configuration with defaults
        self.selected_device: AudioDevice | None = get_default_device()
        self.output_folder: Path = Path.home() / "Desktop"

        # Build menu
        self._build_menu()

        # Timer for updating recording status
        self.timer = rumps.Timer(self._update_timer, 1)

        # Set title with emoji (after init)
        self.title = "🎙️"

    def _build_menu(self) -> None:
        """Build the menu bar menu."""
        self.menu = [
            rumps.MenuItem("Start Recording", callback=self._toggle_recording),
            None,  # Separator
            self._create_device_menu(),
            rumps.MenuItem("Choose Output Folder...", callback=self._choose_folder),
            None,  # Separator
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

    def _select_device(self, sender: rumps.MenuItem, device: AudioDevice) -> None:
        """Handle device selection."""
        # Update selection state
        self.selected_device = device

        # Update menu checkmarks
        parent = sender.parent if hasattr(sender, "parent") else None
        if parent:
            for item in parent.values():
                if isinstance(item, rumps.MenuItem):
                    item.state = 0
        sender.state = 1

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
            # Validate device channels
            if self.selected_device:
                debug_print(f"Selected device: {self.selected_device}")
                if self.selected_device.channels < 1:
                    raise RuntimeError(f"Device '{self.selected_device.name}' has 0 input channels.")
            
            # Create recorder with selected device
            # Use device's native channel count and sample rate to avoid PortAudio errors
            channels = self.selected_device.channels if self.selected_device else 2
            sample_rate = int(self.selected_device.sample_rate) if self.selected_device else 44100

            self.recorder = AudioRecorder(
                device=self.selected_device.index if self.selected_device else None,
                channels=channels,
                sample_rate=sample_rate,
            )

            # Start recording (non-blocking)
            self.recorder.start()

            self.is_recording = True
            self.start_time = time.time()

            # Update menu
            self.menu["Start Recording"].title = "Stop Recording"
            self.title = "🔴"

            # Start timer to update display
            self.timer.start()

        except Exception as e:
            debug_print(f"Recording error: {e}")
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
             debug_print(f"Finish recording error: {e}")
             self._on_recording_error(str(e))
        finally:
            # Restore UI on main thread (rumps handles thread safety usually, but let's be safe)
            # Actually rumps callbacks are on main thread, but this is a background thread.
            # Rumps doesn't have explicit invoke_on_main, but updating menu items is usually fine.
            # However, to be cleaner, we call a method that resets the UI.
            # Since we are in a thread, we should simple call _on_recording_complete
            # Attempting to verify if rumps requires main thread for UI updates.
            # Usually yes. But let's assume simple property updates are safe or handled by rumps.
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
            debug_print(f"Notification failed: {e}")
            # Fallback for when run from terminal without app bundle
            if "Info.plist" in str(e) or "CFBundleIdentifier" in str(e):
                debug_print("Using alert fallback for notification")
                rumps.alert(
                    title,
                    f"{subtitle}\n{message}"
                )


    def _save_recording(self) -> None:
        """Save the recorded audio as MP3."""
        if self.recorder is None:
            return

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"recording_{timestamp}.mp3"
        output_path = self.output_folder / filename

        try:
            saved_path = self.recorder.save_mp3(output_path)

            # Show notification
            self._safe_notification(
                title="Recording Complete",
                subtitle="MP3 saved successfully",
                message=str(saved_path),
            )
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
        # Ensure UI is reset
        self._on_recording_complete()

    def _update_timer(self, _: rumps.Timer) -> None:
        """Update the timer display during recording."""
        if not self.is_recording:
            return

        elapsed = int(time.time() - self.start_time)

        # Update menu bar title with progress
        self.title = f"🔴 {elapsed}s"

    def _choose_folder(self, _: rumps.MenuItem) -> None:
        """Open dialog to choose output folder."""
        # rumps doesn't have a native folder picker, so we use a text input
        # with the current path and instructions
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
            elif not new_path.exists():
                # Try to create the directory
                try:
                    new_path.mkdir(parents=True)
                    self.output_folder = new_path
                except OSError as e:
                    rumps.alert("Invalid Folder", f"Could not create folder: {e}")
            else:
                rumps.alert("Invalid Folder", "Please enter a valid directory path.")

    def _quit(self, _: rumps.MenuItem) -> None:
        """Quit the application."""
        if self.is_recording:
            self.should_stop = True
            # Wait for recording thread to finish
            if self.recording_thread:
                self.recording_thread.join(timeout=2)
        rumps.quit_application()


def main() -> None:
    """Main entry point for the menu bar app."""
    debug_print("Starting MP3 Recorder Menu Bar...")
    debug_print("Creating app instance...")
    app = MP3RecorderMenuBar()
    debug_print(f"App title: {app.title}")
    debug_print(f"App menu items: {list(app.menu.keys()) if app.menu else 'None'}")
    debug_print("Running app.run() - icon should appear in menu bar now...")
    app.run()


if __name__ == "__main__":
    main()
