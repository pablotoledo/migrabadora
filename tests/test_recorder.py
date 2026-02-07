"""Unit tests for the recorder module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from mp3recorder.recorder import AudioRecorder, record_audio


class TestAudioRecorderInit:
    """Tests for AudioRecorder initialization."""

    def test_default_initialization(self):
        """Should initialize with default values."""
        recorder = AudioRecorder()

        assert recorder.device is None
        assert recorder.sample_rate == 44100
        assert recorder.channels == 2
        assert recorder.bitrate == "192k"
        assert recorder._audio_data is None

    def test_custom_initialization(self):
        """Should accept custom parameters."""
        recorder = AudioRecorder(
            device=1,
            sample_rate=48000,
            channels=1,
            bitrate="320k",
        )

        assert recorder.device == 1
        assert recorder.sample_rate == 48000
        assert recorder.channels == 1
        assert recorder.bitrate == "320k"

    def test_device_can_be_string(self):
        """Should accept device name as string."""
        recorder = AudioRecorder(device="BlackHole")

        assert recorder.device == "BlackHole"


class TestAudioRecorderRecord:
    """Tests for AudioRecorder.record method."""

    def test_record_returns_audio_data(self, mock_sounddevice, mock_audio_data):
        """Should return numpy array with recorded audio."""
        recorder = AudioRecorder()
        result = recorder.record(duration=1.0)

        assert isinstance(result, np.ndarray)
        assert result.shape == mock_audio_data.shape

    def test_record_stores_audio_data(self, mock_sounddevice, mock_audio_data):
        """Should store recorded audio in _audio_data."""
        recorder = AudioRecorder()
        recorder.record(duration=1.0)

        assert recorder._audio_data is not None
        np.testing.assert_array_equal(recorder._audio_data, mock_audio_data)

    def test_record_calls_sounddevice_correctly(self, mock_sounddevice):
        """Should call sounddevice.InputStream with correct parameters."""
        recorder = AudioRecorder(
            device=1,
            sample_rate=48000,
            channels=1,
        )
        recorder.record(duration=2.0)

        # The recorder now uses InputStream for streaming recording
        mock_sounddevice["InputStream"].assert_called_once()
        call_kwargs = mock_sounddevice["InputStream"].call_args

        assert call_kwargs.kwargs["samplerate"] == 48000
        assert call_kwargs.kwargs["channels"] == 1
        assert call_kwargs.kwargs["device"] == 1

    def test_record_sleeps_for_duration(self, mock_sounddevice):
        """Should sleep for the specified duration during recording."""
        recorder = AudioRecorder()
        recorder.record(duration=1.0)

        # The record() method calls sd.sleep(duration_ms) after starting
        mock_sounddevice["sleep"].assert_called_once_with(1000)


class TestAudioRecorderGetAudioData:
    """Tests for AudioRecorder.get_audio_data method."""

    def test_returns_none_before_recording(self):
        """Should return None if no recording has been made."""
        recorder = AudioRecorder()

        assert recorder.get_audio_data() is None

    def test_returns_audio_data_after_recording(self, mock_sounddevice, mock_audio_data):
        """Should return audio data after recording."""
        recorder = AudioRecorder()
        recorder.record(duration=1.0)

        result = recorder.get_audio_data()
        assert result is not None
        np.testing.assert_array_equal(result, mock_audio_data)


class TestAudioRecorderSaveMp3:
    """Tests for AudioRecorder.save_mp3 method."""

    def test_raises_error_without_recording(self):
        """Should raise ValueError if no audio recorded."""
        recorder = AudioRecorder()

        with pytest.raises(ValueError, match="No audio data to save"):
            recorder.save_mp3("output.mp3")

    def test_saves_mp3_file(self, mock_sounddevice, mock_audio_data, tmp_path):
        """Should save audio as MP3 file."""
        output_path = tmp_path / "test.mp3"

        with patch("mp3recorder.recorder.AudioSegment") as mock_segment:
            mock_audio_segment = MagicMock()
            mock_segment.from_wav.return_value = mock_audio_segment

            recorder = AudioRecorder()
            recorder.record(duration=1.0)
            result = recorder.save_mp3(output_path)

            assert result == output_path
            mock_audio_segment.export.assert_called_once()

    def test_returns_path_object(self, mock_sounddevice, mock_audio_data, tmp_path):
        """Should return Path object."""
        output_path = tmp_path / "test.mp3"

        with patch("mp3recorder.recorder.AudioSegment") as mock_segment:
            mock_segment.from_wav.return_value = MagicMock()

            recorder = AudioRecorder()
            recorder.record(duration=1.0)
            result = recorder.save_mp3(str(output_path))

            assert isinstance(result, Path)


class TestAudioRecorderSaveWav:
    """Tests for AudioRecorder.save_wav method."""

    def test_raises_error_without_recording(self):
        """Should raise ValueError if no audio recorded."""
        recorder = AudioRecorder()

        with pytest.raises(ValueError, match="No audio data to save"):
            recorder.save_wav("output.wav")

    def test_saves_wav_file(self, mock_sounddevice, mock_audio_data, tmp_path):
        """Should save audio as WAV file."""
        output_path = tmp_path / "test.wav"

        recorder = AudioRecorder()
        recorder.record(duration=1.0)
        result = recorder.save_wav(output_path)

        assert result == output_path
        assert output_path.exists()


class TestRecordAudioFunction:
    """Tests for record_audio convenience function."""

    def test_records_and_saves(self, mock_sounddevice, mock_audio_data, tmp_path):
        """Should record audio and save as MP3."""
        output_path = tmp_path / "test.mp3"

        with patch("mp3recorder.recorder.AudioSegment") as mock_segment:
            mock_segment.from_wav.return_value = MagicMock()

            result = record_audio(
                duration=1.0,
                output_path=output_path,
            )

            assert result == output_path

    def test_accepts_all_parameters(self, mock_sounddevice, mock_audio_data, tmp_path):
        """Should accept all AudioRecorder parameters."""
        output_path = tmp_path / "test.mp3"

        with patch("mp3recorder.recorder.AudioSegment") as mock_segment:
            mock_segment.from_wav.return_value = MagicMock()

            result = record_audio(
                duration=2.0,
                output_path=output_path,
                device=1,
                sample_rate=48000,
                channels=1,
                bitrate="320k",
            )

            assert result == output_path
