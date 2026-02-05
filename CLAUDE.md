# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MP3 Recorder is a minimal terminal-based MP3 audio recorder for macOS. It records audio from any input device (including BlackHole for system audio) and exports to MP3 format.

**External requirements:** FFmpeg (for MP3 encoding), optionally BlackHole (for system audio recording).

## Development Commands

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=mp3recorder --cov-report=term-missing

# Lint
poetry run ruff check src/ tests/

# Auto-fix lint issues
poetry run ruff check --fix src/ tests/

# Format code
poetry run ruff format src/ tests/

# Run the CLI
poetry run mp3recorder list-devices
poetry run mp3recorder record --duration 10 --output recording.mp3
```

## Architecture

```
src/mp3recorder/
├── cli.py         # CLI entry point, argument parsing, command handlers
├── menubar.py     # macOS menu bar app using rumps
├── recorder.py    # AudioRecorder class - core recording and MP3/WAV export
├── devices.py     # Device discovery and selection (AudioDevice dataclass)
├── __init__.py    # Package exports (AudioRecorder, __version__)
└── __main__.py    # Module entry point for `python -m mp3recorder`
```

### Menu Bar App

The menu bar app (`menubar.py`) provides a graphical interface for recording audio from the macOS menu bar:

```bash
# Run the menu bar app
poetry run mp3recorder-menubar
```

**Features:**
- Start/Stop recording from menu bar icon
- Select audio input device from submenu
- Configure recording duration
- Choose output folder for saved recordings
- Real-time recording progress display (🔴 Xs / Ys)
- Native macOS notifications when recording completes

**Debug Mode:**
The app currently runs with `DEBUG = True` enabled for easier troubleshooting. This prints status messages to the terminal.

### Recording Flow

1. `AudioRecorder.record(duration)` captures audio via sounddevice to numpy float32 array
2. `save_mp3()` converts float32 → int16, writes temporary WAV, uses pydub/FFmpeg to encode MP3, deletes temp file
3. Device selection accepts index (int), partial name (string), or None (default device)

### Key Classes

- `AudioRecorder` (recorder.py): Main recording engine with configurable sample_rate, channels, bitrate
- `AudioDevice` (devices.py): Dataclass representing audio input device

## Testing

Tests are in `tests/` and use pytest fixtures from `conftest.py` that mock the sounddevice module. All audio device interactions are mocked—tests don't require actual audio hardware.

```bash
# Run a single test file
poetry run pytest tests/test_recorder.py -v

# Run a specific test
poetry run pytest tests/test_cli.py::test_cmd_record -v
```

## Ruff Configuration

Line length 88, Python 3.10 target. Per-file ignore: `ARG002` in tests (fixtures may have unused args).
