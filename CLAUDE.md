# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MP3 Recorder is a dual-interface macOS application for audio recording with two modes of operation:

1. **Menu Bar App** (`mp3recorder-menubar`): Visual macOS status bar app with GUI controls
2. **CLI Tool** (`mp3recorder`): Terminal-based interface for scripting and automation

Both interfaces record from any input device (including BlackHole for system audio) and export to MP3 format.

**Key Features:**
- **Dual Interface:** Both GUI (menu bar) and CLI modes available.
- **Standalone App:** Bundled with Python and FFmpeg (no external deps required).
- **Smart Audio Routing:** Automatically switches Multi-Output devices to BlackHole.
- **System Audio:** Seamless recording via BlackHole.
- **Robust Selection:** Exclusive device selection logic.
- **Scriptable:** CLI interface for automation and scripting.

## Development Commands

```bash
# Using Makefile (recommended)
make install     # Install dependencies
make dev         # Run the menu bar app
make test        # Run tests with coverage
make test-v      # Run tests with verbose output
make lint        # Run linter
make format      # Format code
make check       # Run lint + test (quick CI check)
make ci          # Full CI check
make clean       # Remove build artifacts
make build-app   # Build standalone .app (PyInstaller)
make dmg         # Create DMG installer

# Direct commands - Menu Bar App
poetry run mp3recorder-menubar  # Run menu bar app

# Direct commands - CLI Interface
poetry run mp3recorder list-devices                    # List audio devices
poetry run mp3recorder record -d 10 -o output.mp3      # Record 10 seconds
poetry run mp3recorder record --device "BlackHole" -d 30 -o recording.mp3

# Run as module
python -m mp3recorder  # Launches menu bar app by default

# Testing
poetry run pytest                                      # Run tests
poetry run pytest -v --cov=mp3recorder                # Verbose with coverage
```

## Architecture

```
src/mp3recorder/
├── __init__.py          # Package exports & version
├── __main__.py          # Entry point for python -m mp3recorder
├── cli.py               # CLI interface (argparse) with record/list-devices commands
├── menubar.py           # macOS menu bar app (rumps) + Smart Logic
├── recorder.py          # AudioRecorder class - core recording engine
├── devices.py           # Device discovery & AudioDevice dataclass
├── config.py            # Persistent configuration (JSON)
├── dependencies.py      # Bundled FFmpeg & BlackHole detection
├── logging_config.py    # Centralized logging setup
└── startup.py           # LaunchAgent management (auto-start)

scripts/
├── build.sh             # Build script
├── create_dmg.sh        # DMG creation script
└── uninstall.sh         # App uninstall script

tests/
├── conftest.py          # Pytest fixtures and configuration
├── test_cli.py          # CLI interface tests
├── test_config.py       # Configuration management tests
├── test_dependencies.py # FFmpeg/BlackHole detection tests
├── test_devices.py      # Audio device discovery tests
├── test_logging_config.py # Logging setup tests
├── test_recorder.py     # Core recording engine tests
└── test_startup.py      # LaunchAgent management tests

docs/
├── blackhole_setup.md   # BlackHole installation guide
├── quickstart.md        # Quick start guide
└── usage.md             # Detailed usage instructions

Packaging:
├── MP3 Recorder.spec    # PyInstaller specification
├── setup_app.py         # py2app setup (deprecated/broken on macOS 26)
├── pyproject.toml       # Poetry configuration & dependencies
└── Makefile             # Development commands
```

### Menu Bar App Features
- **Smart Recording**: Auto-detects Multi-Output devices and routes via BlackHole.
- **Visual Feedback**: 🔴 MM:SS timer in menu bar.
- **Quality Control**: 128k/192k/256k/320k bitrate selection (Radio behavior).
- **Device Management**: Lists all devices (input/output/aggregate).
- **Recent Recordings**: Quick access to last 5 files.
- **Auto-Start**: Optional LaunchAgent for startup at login.

### CLI Interface Features
- **Device Listing**: `mp3recorder list-devices` - enumerate all audio devices.
- **Fixed Duration Recording**: Record with `-d/--duration` flag.
- **Device Selection**: Record from specific device with `--device` flag.
- **Quality Control**: Choose bitrate (128k/192k/256k/320k) with `--bitrate`.
- **Sample Rate**: Configure with `--sample-rate` (default: 44100).
- **Channels**: Mono or stereo with `--channels` (1 or 2).
- **Scriptable**: Ideal for automation and batch processing.

### Key Modules
| Module | Purpose |
|--------|---------|
| `cli.py` | Terminal CLI with argparse (list-devices, record commands) |
| `menubar.py` | Menu bar UI logic, Smart Routing, Error Handling |
| `recorder.py` | Audio capture (sounddevice), Encoding (bundled FFmpeg) |
| `devices.py` | Audio device discovery & enumeration |
| `config.py` | Persistent JSON config (bitrate, device, output folder) |
| `dependencies.py` | Bundled vs system FFmpeg resolution, BlackHole detection |
| `startup.py` | LaunchAgent installation/uninstallation for auto-start |
| `logging_config.py` | Centralized logging to ~/Library/Logs/MP3Recorder/ |
| `MP3 Recorder.spec` | PyInstaller build config |

## Testing
Tests mock `sounddevice` and external dependencies so no hardware or FFmpeg is required.

**Test Coverage:**
- `test_cli.py`: CLI argument parsing and command execution
- `test_recorder.py`: Core audio recording engine
- `test_devices.py`: Device discovery and enumeration
- `test_config.py`: Configuration persistence and defaults
- `test_dependencies.py`: FFmpeg/BlackHole detection logic
- `test_startup.py`: LaunchAgent installation/uninstallation
- `test_logging_config.py`: Logging setup and directory creation
- `conftest.py`: Shared fixtures (temp dirs, mock configs)

```bash
make test              # Run all tests with coverage
make test-v            # Verbose test output
make check             # Lint + test (quick CI check)
pytest tests/          # Direct pytest invocation
```

## Entry Points

The project defines two Poetry scripts in `pyproject.toml`:

```toml
[tool.poetry.scripts]
mp3recorder = "mp3recorder.cli:main"              # CLI interface
mp3recorder-menubar = "mp3recorder.menubar:main"  # Menu bar app
```

Additionally, `python -m mp3recorder` launches the menu bar app via `__main__.py`.

## Building (PyInstaller)
The app is built as a self-contained bundle.
```bash
make build-app   # Creates dist/MP3 Recorder.app
make dmg         # Creates dist/MP3 Recorder.dmg
```

## Runtime Locations
| Type | Path |
|------|------|
| Config | `~/Library/Application Support/MP3Recorder/config.json` |
| Logs | `~/Library/Logs/MP3Recorder/mp3recorder.log` |
| LaunchAgent | `~/Library/LaunchAgents/com.mp3recorder.menubar.plist` |
| Default Output | `~/Downloads/` (configurable via menu bar app) |

## Documentation
| File | Description |
|------|-------------|
| `docs/blackhole_setup.md` | Complete BlackHole installation guide |
| `docs/quickstart.md` | Quick start guide for new users |
| `docs/usage.md` | Detailed usage instructions |
| `README.md` | Project overview and basic usage |

## Scripts

The `scripts/` directory contains build and maintenance scripts:

| Script | Purpose |
|--------|---------|
| `build.sh` | Alternative build script |
| `create_dmg.sh` | Creates DMG installer from .app bundle |
| `uninstall.sh` | Complete app uninstallation (app, config, logs, LaunchAgent) |

Usage:
```bash
./scripts/create_dmg.sh  # Create DMG (requires built .app)
./scripts/uninstall.sh   # Uninstall MP3 Recorder completely
```

## Dependencies

**Core:**
- `sounddevice`: Audio capture from devices
- `numpy`: Audio data handling
- `pydub`: MP3 encoding (requires FFmpeg)
- `rumps`: macOS menu bar interface
- `imageio-ffmpeg`: Bundled FFmpeg for standalone builds

**Dev:**
- `pytest` + `pytest-cov`: Testing framework
- `ruff`: Linting and formatting
- `pyinstaller`: Standalone .app bundling
- `py2app`: Alternative bundler (currently broken on macOS 26+)

## Ruff Configuration
Line length 88, Python 3.10 target. Per-file ignore: `ARG002` in tests (fixture arguments).

## Important Notes

### Two Interfaces, Shared Core
The project has **two distinct user interfaces** but they share the same core recording engine (`recorder.py`):
- **CLI** (`mp3recorder`): For terminal users, automation, and scripting. Fixed duration recordings.
- **Menu Bar App** (`mp3recorder-menubar`): For GUI users with visual controls. Supports indefinite recording (start/stop).

### Build System
- **Primary**: PyInstaller (`make build-app`) - actively maintained, working on macOS 26+
- **Deprecated**: py2app (`setup_app.py`) - broken on macOS 26+, kept for reference

### FFmpeg Handling
The app bundles FFmpeg via `imageio-ffmpeg` for standalone builds, but will use system FFmpeg if available during development. The `dependencies.py` module handles this resolution.

### BlackHole Integration
BlackHole is optional but enables system audio recording. The menu bar app has smart routing logic that auto-switches Multi-Output devices to use BlackHole as the input source.

### Configuration
- Menu bar app saves preferences to `~/Library/Application Support/MP3Recorder/config.json`
- CLI uses command-line flags exclusively (no persistent config)
- Config includes: default device, bitrate, output folder, startup preference

### Testing Philosophy
All tests mock hardware dependencies (`sounddevice`, FFmpeg) so they can run in CI without audio devices or FFmpeg installed.
