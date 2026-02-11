"""Pytest fixtures for mp3recorder tests."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest


@pytest.fixture
def mock_audio_data():
    """Generate mock audio data for testing."""
    # 1 second of stereo audio at 44100 Hz
    duration = 1.0
    sample_rate = 44100
    samples = int(duration * sample_rate)

    # Generate sine wave test signal
    t = np.linspace(0, duration, samples, dtype=np.float32)
    left = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    right = np.sin(2 * np.pi * 880 * t)  # 880 Hz sine wave

    return np.column_stack((left, right)).astype(np.float32)


@pytest.fixture
def mock_devices():
    """Mock device list for testing."""
    return [
        {
            "name": "Built-in Microphone",
            "max_input_channels": 1,
            "max_output_channels": 0,
            "default_samplerate": 48000.0,
        },
        {
            "name": "BlackHole 2ch",
            "max_input_channels": 2,
            "max_output_channels": 2,
            "default_samplerate": 48000.0,
        },
        {
            "name": "USB Audio Device",
            "max_input_channels": 2,
            "max_output_channels": 2,
            "default_samplerate": 44100.0,
        },
        {
            "name": "External Speakers",
            "max_input_channels": 0,
            "max_output_channels": 2,
            "default_samplerate": 44100.0,
        },
    ]


class MockInputStream:
    """Mock for sd.InputStream that simulates streaming recording."""

    def __init__(self, callback=None, audio_data=None, **kwargs):
        self.callback = callback
        self.audio_data = audio_data
        self.started = False
        self.closed = False

    def start(self):
        """Start the mock stream and feed audio data via callback."""
        self.started = True
        # Simulate feeding audio data in chunks via callback
        if self.callback and self.audio_data is not None:
            # Feed audio in one chunk (simulating real-time recording)
            self.callback(self.audio_data, len(self.audio_data), None, None)

    def stop(self):
        """Stop the mock stream."""
        self.started = False

    def close(self):
        """Close the mock stream."""
        self.closed = True


@pytest.fixture
def mock_sounddevice(mock_devices, mock_audio_data):
    """Patch sounddevice module for testing.

    This fixture mocks both the old sd.rec() API and the new InputStream API
    used by the start/stop recording methods.
    """
    with (
        patch("sounddevice.query_devices") as mock_query,
        patch("sounddevice.default", new=MagicMock()) as mock_default,
        patch("sounddevice.rec") as mock_rec,
        patch("sounddevice.wait") as mock_wait,
        patch("sounddevice.sleep") as mock_sleep,
        patch("sounddevice.InputStream") as mock_input_stream,
    ):
        mock_query.return_value = mock_devices
        mock_default.device = (0, 0)  # Default input and output device indices
        mock_rec.return_value = mock_audio_data

        # Configure InputStream mock to create MockInputStream instances
        def create_mock_stream(**kwargs):
            callback = kwargs.pop("callback", None)
            return MockInputStream(
                callback=callback, audio_data=mock_audio_data, **kwargs
            )

        mock_input_stream.side_effect = create_mock_stream

        yield {
            "query_devices": mock_query,
            "default": mock_default,
            "rec": mock_rec,
            "wait": mock_wait,
            "sleep": mock_sleep,
            "InputStream": mock_input_stream,
        }
