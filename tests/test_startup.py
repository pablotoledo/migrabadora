"""Unit tests for the startup module."""

import plistlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mp3recorder.startup import (
    LAUNCH_AGENT_LABEL,
    get_launch_agent_executable,
    get_launch_agent_path,
    install_launch_agent,
    is_launch_agent_installed,
    uninstall_launch_agent,
)


@pytest.fixture
def temp_launch_agents_dir(tmp_path):
    """Use a temporary directory for LaunchAgents during tests."""
    import mp3recorder.startup as startup

    original_dir = startup.LAUNCH_AGENTS_DIR
    original_path = startup.LAUNCH_AGENT_PATH

    # Override the module-level constants
    startup.LAUNCH_AGENTS_DIR = tmp_path
    startup.LAUNCH_AGENT_PATH = tmp_path / f"{LAUNCH_AGENT_LABEL}.plist"

    yield tmp_path

    # Restore original values
    startup.LAUNCH_AGENTS_DIR = original_dir
    startup.LAUNCH_AGENT_PATH = original_path


class TestIsLaunchAgentInstalled:
    """Tests for is_launch_agent_installed function."""

    def test_returns_false_when_not_installed(self, temp_launch_agents_dir):
        """Should return False when plist doesn't exist."""
        result = is_launch_agent_installed()

        assert result is False

    def test_returns_true_when_installed(self, temp_launch_agents_dir):
        """Should return True when plist exists."""
        import mp3recorder.startup as startup

        # Create the plist file
        startup.LAUNCH_AGENT_PATH.write_text("test")

        result = is_launch_agent_installed()

        assert result is True


class TestInstallLaunchAgent:
    """Tests for install_launch_agent function."""

    def test_creates_plist_file(self, temp_launch_agents_dir):
        """Should create a valid plist file."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock()

            result = install_launch_agent("/path/to/app")

            import mp3recorder.startup as startup

            assert result is True
            assert startup.LAUNCH_AGENT_PATH.exists()

    def test_plist_contains_correct_label(self, temp_launch_agents_dir):
        """Should create plist with correct label."""
        with patch("subprocess.run"):
            install_launch_agent("/path/to/app")

            import mp3recorder.startup as startup

            with startup.LAUNCH_AGENT_PATH.open("rb") as f:
                plist = plistlib.load(f)

            assert plist["Label"] == LAUNCH_AGENT_LABEL

    def test_plist_contains_run_at_load(self, temp_launch_agents_dir):
        """Should create plist with RunAtLoad set to True."""
        with patch("subprocess.run"):
            install_launch_agent("/path/to/app")

            import mp3recorder.startup as startup

            with startup.LAUNCH_AGENT_PATH.open("rb") as f:
                plist = plistlib.load(f)

            assert plist["RunAtLoad"] is True

    def test_handles_app_bundle_path(self, temp_launch_agents_dir):
        """Should handle .app bundle paths correctly."""
        with patch("subprocess.run"):
            # Pass a .app path
            result = install_launch_agent("/Applications/MP3 Recorder.app")

            assert result is True

    def test_creates_directory_if_needed(self, temp_launch_agents_dir):
        """Should create LaunchAgents directory if it doesn't exist."""
        import mp3recorder.startup as startup

        subdir = temp_launch_agents_dir / "subdir"
        startup.LAUNCH_AGENTS_DIR = subdir
        startup.LAUNCH_AGENT_PATH = subdir / f"{LAUNCH_AGENT_LABEL}.plist"

        with patch("subprocess.run"):
            result = install_launch_agent("/path/to/app")

            assert result is True
            assert subdir.exists()


class TestUninstallLaunchAgent:
    """Tests for uninstall_launch_agent function."""

    def test_removes_plist_file(self, temp_launch_agents_dir):
        """Should remove the plist file."""
        import mp3recorder.startup as startup

        # Create a plist file first
        plist_content = {
            "Label": LAUNCH_AGENT_LABEL,
            "ProgramArguments": ["/path/to/app"],
            "RunAtLoad": True,
        }
        with startup.LAUNCH_AGENT_PATH.open("wb") as f:
            plistlib.dump(plist_content, f)

        with patch("subprocess.run"):
            result = uninstall_launch_agent()

            assert result is True
            assert not startup.LAUNCH_AGENT_PATH.exists()

    def test_returns_true_when_not_installed(self, temp_launch_agents_dir):
        """Should return True when plist doesn't exist."""
        result = uninstall_launch_agent()

        assert result is True

    def test_calls_launchctl_unload(self, temp_launch_agents_dir):
        """Should call launchctl unload."""
        import mp3recorder.startup as startup

        # Create a plist file
        plist_content = {"Label": LAUNCH_AGENT_LABEL, "ProgramArguments": ["/test"]}
        with startup.LAUNCH_AGENT_PATH.open("wb") as f:
            plistlib.dump(plist_content, f)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock()

            uninstall_launch_agent()

            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "launchctl" in call_args
            assert "unload" in call_args


class TestGetLaunchAgentPath:
    """Tests for get_launch_agent_path function."""

    def test_returns_path(self):
        """Should return a Path object."""
        path = get_launch_agent_path()

        assert isinstance(path, Path)
        assert LAUNCH_AGENT_LABEL in str(path)


class TestGetLaunchAgentExecutable:
    """Tests for get_launch_agent_executable function."""

    def test_returns_none_when_not_installed(self, temp_launch_agents_dir):
        """Should return None when plist doesn't exist."""
        result = get_launch_agent_executable()

        assert result is None

    def test_returns_executable_path(self, temp_launch_agents_dir):
        """Should return the executable path from plist."""
        import mp3recorder.startup as startup

        plist_content = {
            "Label": LAUNCH_AGENT_LABEL,
            "ProgramArguments": ["/path/to/executable", "--arg"],
        }
        with startup.LAUNCH_AGENT_PATH.open("wb") as f:
            plistlib.dump(plist_content, f)

        result = get_launch_agent_executable()

        assert result == "/path/to/executable"


class TestUninstallApp:
    """Tests for uninstall_app function."""

    def test_returns_results_dict(self, temp_launch_agents_dir):
        """Should return dict with all components."""
        from mp3recorder.startup import uninstall_app

        with patch("mp3recorder.startup.uninstall_launch_agent", return_value=True):
            results = uninstall_app(remove_config=False, remove_logs=False)

            assert "launch_agent" in results
            assert "config" in results
            assert "logs" in results

    def test_uninstalls_launch_agent(self, temp_launch_agents_dir):
        """Should call uninstall_launch_agent."""
        from mp3recorder.startup import uninstall_app

        with patch("mp3recorder.startup.uninstall_launch_agent") as mock_uninstall:
            mock_uninstall.return_value = True

            results = uninstall_app(remove_config=False, remove_logs=False)

            mock_uninstall.assert_called_once()
            assert results["launch_agent"] is True


class TestGetUninstallSummary:
    """Tests for get_uninstall_summary function."""

    def test_returns_string(self, temp_launch_agents_dir):
        """Should return a string."""
        from mp3recorder.startup import get_uninstall_summary

        with patch("mp3recorder.config.CONFIG_DIR") as mock_config:
            mock_config.exists.return_value = False
            with patch("mp3recorder.logging_config.LOG_DIR") as mock_log:
                mock_log.exists.return_value = False

                result = get_uninstall_summary()

                assert isinstance(result, str)

    def test_shows_no_data_message(self, temp_launch_agents_dir):
        """Should show no data message when nothing to remove."""
        from mp3recorder.startup import get_uninstall_summary

        with patch("mp3recorder.startup.LAUNCH_AGENT_PATH") as mock_la:
            mock_la.exists.return_value = False
            with patch("mp3recorder.config.CONFIG_DIR") as mock_config:
                mock_config.exists.return_value = False
                with patch("mp3recorder.logging_config.LOG_DIR") as mock_log:
                    mock_log.exists.return_value = False

                    result = get_uninstall_summary()

                    assert "No MP3 Recorder data found" in result
