"""Audio device utilities for MP3 Recorder."""

from dataclasses import dataclass

import sounddevice as sd


@dataclass
class AudioDevice:
    """Represents an audio input device."""

    index: int
    name: str
    channels: int
    sample_rate: float
    is_default: bool = False


def list_audio_devices() -> list[AudioDevice]:
    """List all available audio input devices.

    Returns:
        List of AudioDevice objects representing available input devices.
    """
    devices = []
    default_input = sd.default.device[0]

    for idx, device in enumerate(sd.query_devices()):
        # Include all devices, even if they report 0 input channels (user request)
        # Some virtual devices or aggregates might report 0 but still work,
        # or the user effectively wants to try them.
        devices.append(
            AudioDevice(
                index=idx,
                name=device["name"],
                channels=device["max_input_channels"],
                sample_rate=device["default_samplerate"],
                is_default=(idx == default_input),
            )
        )

    return devices


def get_device_by_name(name: str) -> AudioDevice | None:
    """Find an audio device by partial name match.

    Args:
        name: Partial name to search for (case-insensitive).

    Returns:
        AudioDevice if found, None otherwise.
    """
    name_lower = name.lower()
    devices = list_audio_devices()

    for device in devices:
        if name_lower in device.name.lower():
            return device

    return None


def get_default_device() -> AudioDevice | None:
    """Get the default audio input device.

    Returns:
        Default AudioDevice if available, None otherwise.
    """
    devices = list_audio_devices()

    for device in devices:
        if device.is_default:
            return device

    # Fallback to first device if no default
    return devices[0] if devices else None
