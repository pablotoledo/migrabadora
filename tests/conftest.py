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


@pytest.fixture
def mock_sounddevice(mock_devices, mock_audio_data):
    """Patch sounddevice module for testing."""
    with patch("sounddevice.query_devices") as mock_query, \
         patch("sounddevice.default", new=MagicMock()) as mock_default, \
         patch("sounddevice.rec") as mock_rec, \
         patch("sounddevice.wait") as mock_wait:

        mock_query.return_value = mock_devices
        mock_default.device = (0, 0)  # Default input and output device indices
        mock_rec.return_value = mock_audio_data

        yield {
            "query_devices": mock_query,
            "default": mock_default,
            "rec": mock_rec,
            "wait": mock_wait,
        }
