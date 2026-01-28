"""Unit tests for the devices module."""


from mp3recorder.devices import (
    AudioDevice,
    get_default_device,
    get_device_by_name,
    list_audio_devices,
)


class TestListAudioDevices:
    """Tests for list_audio_devices function."""

    def test_returns_list_of_audio_devices(self, mock_sounddevice):
        """Should return a list of AudioDevice objects."""
        devices = list_audio_devices()

        assert isinstance(devices, list)
        assert all(isinstance(d, AudioDevice) for d in devices)

    def test_filters_input_devices_only(self, mock_sounddevice):
        """Should only include devices with input channels."""
        devices = list_audio_devices()

        # Original mock has 3 input devices and 1 output-only device
        assert len(devices) == 3

        # All returned devices should have input channels
        for device in devices:
            assert device.channels > 0

    def test_includes_device_properties(self, mock_sounddevice):
        """Should include all device properties."""
        devices = list_audio_devices()

        blackhole = next((d for d in devices if "BlackHole" in d.name), None)
        assert blackhole is not None
        assert blackhole.channels == 2
        assert blackhole.sample_rate == 48000.0

    def test_marks_default_device(self, mock_sounddevice):
        """Should mark the default input device."""
        devices = list_audio_devices()

        default_devices = [d for d in devices if d.is_default]
        assert len(default_devices) == 1
        assert default_devices[0].index == 0

    def test_returns_empty_list_when_no_devices(self, mock_sounddevice):
        """Should return empty list when no input devices exist."""
        mock_sounddevice["query_devices"].return_value = []

        devices = list_audio_devices()
        assert devices == []


class TestGetDeviceByName:
    """Tests for get_device_by_name function."""

    def test_finds_device_by_exact_name(self, mock_sounddevice):
        """Should find device by exact name match."""
        device = get_device_by_name("BlackHole 2ch")

        assert device is not None
        assert device.name == "BlackHole 2ch"

    def test_finds_device_by_partial_name(self, mock_sounddevice):
        """Should find device by partial name match."""
        device = get_device_by_name("BlackHole")

        assert device is not None
        assert "BlackHole" in device.name

    def test_case_insensitive_search(self, mock_sounddevice):
        """Should perform case-insensitive search."""
        device = get_device_by_name("blackhole")

        assert device is not None
        assert "BlackHole" in device.name

    def test_returns_none_for_non_existent_device(self, mock_sounddevice):
        """Should return None when device not found."""
        device = get_device_by_name("NonExistent Device")

        assert device is None


class TestGetDefaultDevice:
    """Tests for get_default_device function."""

    def test_returns_default_device(self, mock_sounddevice):
        """Should return the default input device."""
        device = get_default_device()

        assert device is not None
        assert device.is_default is True

    def test_returns_first_device_when_no_default(self, mock_sounddevice):
        """Should return first device when no default is set."""
        # Set default to invalid index
        mock_sounddevice["default"].device = (-1, -1)

        device = get_default_device()

        # Should return first available device
        assert device is not None

    def test_returns_none_when_no_devices(self, mock_sounddevice):
        """Should return None when no input devices exist."""
        mock_sounddevice["query_devices"].return_value = []

        device = get_default_device()
        assert device is None


class TestAudioDeviceDataclass:
    """Tests for AudioDevice dataclass."""

    def test_creates_device_with_all_fields(self):
        """Should create device with all required fields."""
        device = AudioDevice(
            index=0,
            name="Test Device",
            channels=2,
            sample_rate=44100.0,
            is_default=True,
        )

        assert device.index == 0
        assert device.name == "Test Device"
        assert device.channels == 2
        assert device.sample_rate == 44100.0
        assert device.is_default is True

    def test_default_is_default_false(self):
        """Should default is_default to False."""
        device = AudioDevice(
            index=0,
            name="Test Device",
            channels=2,
            sample_rate=44100.0,
        )

        assert device.is_default is False
