"""Audio recorder module for MP3 Recorder."""

import logging
import tempfile
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from pydub import AudioSegment

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Records audio from an input device and exports to MP3."""

    def __init__(
        self,
        device: int | str | None = None,
        sample_rate: int = 44100,
        channels: int = 2,
        bitrate: str = "192k",
    ) -> None:
        """Initialize the audio recorder.

        Args:
            device: Device index, name, or None for default device.
            sample_rate: Sample rate in Hz (default: 44100).
            channels: Number of channels (1=mono, 2=stereo, default: 2).
            bitrate: MP3 bitrate as string (default: "192k").
        """
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self.bitrate = bitrate
        self._audio_data: np.ndarray | None = None
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None

    def start(self) -> None:
        """Start indefinite recording."""
        self._frames = []
        self._audio_data = None
        
        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.device,
                dtype=np.float32,
                callback=self._callback,
            )
            self._stream.start()
        except Exception as e:
            raise RuntimeError(f"Failed to start recording: {e}") from e

    def stop(self) -> np.ndarray:
        """Stop recording and return the recorded audio data."""
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        
        if self._frames:
            self._audio_data = np.concatenate(self._frames)
        else:
            self._audio_data = np.zeros((0, self.channels), dtype=np.float32)
            
        return self._audio_data

    def _callback(self, indata: np.ndarray, _frames: int, _time, status: sd.CallbackFlags) -> None:
        """Callback for collecting audio frames."""
        if status:
            logger.warning(f"Recording status: {status}")
        self._frames.append(indata.copy())

    def record(self, duration: float) -> np.ndarray:
        """Record audio for the specified duration.

        Args:
            duration: Recording duration in seconds.

        Returns:
            NumPy array containing the recorded audio data.

        Raises:
            RuntimeError: If recording fails.
        """
        try:
            self.start()
            sd.sleep(int(duration * 1000))
            return self.stop()
        except Exception as e:
            raise RuntimeError(f"Recording failed: {e}") from e

    def get_audio_data(self) -> np.ndarray | None:
        """Get the last recorded audio data.

        Returns:
            NumPy array with audio data, or None if no recording exists.
        """
        return self._audio_data

    def save_mp3(self, output_path: str | Path) -> Path:
        """Save the recorded audio as an MP3 file.

        Args:
            output_path: Path where the MP3 file will be saved.

        Returns:
            Path to the saved MP3 file.

        Raises:
            ValueError: If no audio has been recorded.
            RuntimeError: If MP3 encoding fails.
        """
        if self._audio_data is None:
            raise ValueError("No audio data to save. Record audio first.")

        output_path = Path(output_path)

        # Convert float32 audio to int16 for WAV
        audio_int16 = (self._audio_data * 32767).astype(np.int16)

        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            tmp_wav_path = Path(tmp_wav.name)

        try:
            # Save as WAV first using built-in wave module
            self._write_wav(tmp_wav_path, audio_int16)

            # Convert to MP3 using pydub
            audio_segment = AudioSegment.from_wav(str(tmp_wav_path))
            audio_segment.export(
                str(output_path),
                format="mp3",
                bitrate=self.bitrate,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to save MP3: {e}") from e
        finally:
            # Clean up temporary WAV file
            tmp_wav_path.unlink(missing_ok=True)

        return output_path

    def _write_wav(self, path: Path, audio_int16: np.ndarray) -> None:
        """Write audio data to WAV file using built-in wave module.

        Args:
            path: Path to write the WAV file.
            audio_int16: Audio data as int16 numpy array.
        """
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)  # 16-bit = 2 bytes
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

    def save_wav(self, output_path: str | Path) -> Path:
        """Save the recorded audio as a WAV file.

        Args:
            output_path: Path where the WAV file will be saved.

        Returns:
            Path to the saved WAV file.

        Raises:
            ValueError: If no audio has been recorded.
        """
        if self._audio_data is None:
            raise ValueError("No audio data to save. Record audio first.")

        output_path = Path(output_path)

        # Convert float32 audio to int16 for WAV
        audio_int16 = (self._audio_data * 32767).astype(np.int16)
        self._write_wav(output_path, audio_int16)

        return output_path


def record_audio(
    duration: float,
    output_path: str | Path,
    device: int | str | None = None,
    sample_rate: int = 44100,
    channels: int = 2,
    bitrate: str = "192k",
) -> Path:
    """Convenience function to record audio and save as MP3.

    Args:
        duration: Recording duration in seconds.
        output_path: Path where the MP3 file will be saved.
        device: Device index, name, or None for default device.
        sample_rate: Sample rate in Hz (default: 44100).
        channels: Number of channels (default: 2).
        bitrate: MP3 bitrate (default: "192k").

    Returns:
        Path to the saved MP3 file.
    """
    recorder = AudioRecorder(
        device=device,
        sample_rate=sample_rate,
        channels=channels,
        bitrate=bitrate,
    )
    recorder.record(duration)
    return recorder.save_mp3(output_path)
