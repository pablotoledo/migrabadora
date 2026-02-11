"""Unit tests for the CLI module."""

import argparse
from unittest.mock import MagicMock, patch

from mp3recorder.cli import cmd_list_devices, cmd_record, create_parser, main


class TestCreateParser:
    """Tests for create_parser function."""

    def test_creates_parser(self):
        """Should create an ArgumentParser."""
        parser = create_parser()

        assert isinstance(parser, argparse.ArgumentParser)

    def test_has_list_devices_command(self):
        """Should have list-devices subcommand."""
        parser = create_parser()
        args = parser.parse_args(["list-devices"])

        assert args.command == "list-devices"

    def test_has_record_command(self):
        """Should have record subcommand."""
        parser = create_parser()
        args = parser.parse_args(["record", "-d", "10", "-o", "out.mp3"])

        assert args.command == "record"
        assert args.duration == 10.0
        assert args.output == "out.mp3"

    def test_record_command_defaults(self):
        """Should have default values for optional arguments."""
        parser = create_parser()
        args = parser.parse_args(["record", "-d", "5", "-o", "test.mp3"])

        assert args.device is None
        assert args.sample_rate == 44100
        assert args.channels == 2
        assert args.bitrate == 192


class TestCmdListDevices:
    """Tests for cmd_list_devices function."""

    def test_lists_devices(self, mock_sounddevice, capsys):
        """Should print device list."""
        args = argparse.Namespace()
        result = cmd_list_devices(args)

        captured = capsys.readouterr()
        assert "Available Audio Input Devices" in captured.out
        assert result == 0

    def test_returns_error_when_no_devices(self, mock_sounddevice, capsys):
        """Should return 1 when no devices found."""
        mock_sounddevice["query_devices"].return_value = []

        args = argparse.Namespace()
        result = cmd_list_devices(args)

        captured = capsys.readouterr()
        assert "No audio input devices found" in captured.out
        assert result == 1


class TestCmdRecord:
    """Tests for cmd_record function."""

    def test_record_with_default_device(
        self, mock_sounddevice, mock_audio_data, tmp_path
    ):
        """Should record with default device."""
        output_file = tmp_path / "test.mp3"

        with patch("mp3recorder.cli.AudioRecorder") as mock_recorder_class:
            mock_recorder = MagicMock()
            mock_recorder_class.return_value = mock_recorder
            mock_recorder.save_mp3.return_value = output_file

            args = argparse.Namespace(
                duration=1.0,
                output=str(output_file),
                device=None,
                sample_rate=44100,
                channels=2,
                bitrate=192,
            )

            result = cmd_record(args)

            assert result == 0
            mock_recorder.record.assert_called_once_with(1.0)

    def test_record_with_named_device(
        self, mock_sounddevice, mock_audio_data, tmp_path
    ):
        """Should record with specified device."""
        output_file = tmp_path / "test.mp3"

        with patch("mp3recorder.cli.AudioRecorder") as mock_recorder_class:
            mock_recorder = MagicMock()
            mock_recorder_class.return_value = mock_recorder
            mock_recorder.save_mp3.return_value = output_file

            args = argparse.Namespace(
                duration=5.0,
                output=str(output_file),
                device="BlackHole",
                sample_rate=48000,
                channels=2,
                bitrate=320,
            )

            result = cmd_record(args)

            assert result == 0
            # Should use device index from get_device_by_name
            mock_recorder_class.assert_called_once()

    def test_returns_error_for_unknown_device(self, mock_sounddevice, capsys):
        """Should return 1 when device not found."""
        args = argparse.Namespace(
            duration=5.0,
            output="test.mp3",
            device="NonExistent Device",
            sample_rate=44100,
            channels=2,
            bitrate=192,
        )

        result = cmd_record(args)

        captured = capsys.readouterr()
        assert "not found" in captured.out
        assert result == 1


class TestMain:
    """Tests for main entry point."""

    def test_shows_help_with_no_command(self, capsys):
        """Should show help when no command provided."""
        with patch("sys.argv", ["mp3recorder"]):
            result = main()

            assert result == 0

    def test_calls_list_devices(self, mock_sounddevice):
        """Should call list-devices command."""
        with patch("sys.argv", ["mp3recorder", "list-devices"]):
            result = main()

            assert result == 0
