# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MP3 Recorder is a macOS menu bar application for audio recording. It records from any input device (including BlackHole for system audio) and exports to MP3 format.

**External requirements:** FFmpeg (for MP3 encoding), optionally BlackHole (for system audio recording).

## Development Commands

```bash
# Using Makefile (recommended)
make install     # Install dependencies
make dev         # Run the menu bar app
make test        # Run tests with coverage
make lint        # Run linter
make format      # Format code
make build-app   # Build macOS .app bundle
make dmg         # Create DMG installer

# Direct commands
poetry run mp3recorder-menubar  # Run menu bar app
poetry run mp3recorder record --duration 10  # CLI recording
```

## Architecture

```
src/mp3recorder/
├── __init__.py          # Package exports (AudioRecorder, __version__)
├── __main__.py          # Module entry point
├── cli.py               # CLI argument parsing and commands
├── menubar.py           # macOS menu bar app (rumps)
├── recorder.py          # AudioRecorder class - core recording engine
├── devices.py           # Device discovery (AudioDevice dataclass)
├── config.py            # Persistent configuration (JSON)
├── dependencies.py      # FFmpeg/BlackHole detection and helpers
├── logging_config.py    # Centralized logging setup
└── startup.py           # LaunchAgent management (auto-start)

scripts/
├── build.sh             # Build the .app bundle
├── create_dmg.sh        # Create DMG installer
└── uninstall.sh         # Complete uninstallation

tests/
├── conftest.py          # Pytest fixtures (mock sounddevice)
├── test_*.py            # Unit tests for each module
```

### Menu Bar App Features

- **Recording**: Start/Stop with visual feedback (🔴 MM:SS timer)
- **Audio Quality**: 128k/192k/256k/320k bitrate selection
- **Device Selection**: Choose input device from submenu
- **Recent Recordings**: Quick access to last 5 recordings
- **Setup Guide**: FFmpeg and BlackHole installation help
- **Start at Login**: Automatic startup via LaunchAgent
- **Persistent Config**: Settings saved to `~/Library/Application Support/MP3Recorder/`
- **Logging**: Rotating logs at `~/Library/Logs/MP3Recorder/`

### Key Modules

| Module | Purpose |
|--------|---------|
| `recorder.py` | Core audio capture via sounddevice, MP3/WAV export |
| `config.py` | AppConfig dataclass, JSON persistence |
| `dependencies.py` | FFmpeg/BlackHole detection, install instructions |
| `startup.py` | LaunchAgent install/uninstall for auto-start |
| `logging_config.py` | RotatingFileHandler setup |

## Testing

Tests mock the sounddevice module—no actual audio hardware needed.

```bash
make test              # Run all tests with coverage
make test-v            # Verbose output
poetry run pytest tests/test_recorder.py -v  # Single file
```

## Building

```bash
make build-app   # Build MP3 Recorder.app to dist/
make dmg         # Create DMG with drag-to-Applications
```

## Config Locations

| Type | Path |
|------|------|
| Config | `~/Library/Application Support/MP3Recorder/config.json` |
| Logs | `~/Library/Logs/MP3Recorder/mp3recorder.log` |
| LaunchAgent | `~/Library/LaunchAgents/com.mp3recorder.menubar.plist` |

## Ruff Configuration

Line length 88, Python 3.10 target. Per-file ignore: `ARG002` in tests.
