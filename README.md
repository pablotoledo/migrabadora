# MP3 Recorder

Minimal terminal-based MP3 audio recorder for macOS, designed to work with virtual audio devices like BlackHole.

## Features

- 🎙️ Record audio from any input device
- 🔊 Support for BlackHole virtual audio (record system audio)
- 📦 Export directly to MP3 format
- ⚡ Simple CLI interface
- 🎛️ Configurable sample rate, channels, and bitrate

## Requirements

- Python 3.10+
- FFmpeg (required for MP3 encoding)
- BlackHole (optional, for recording system audio)

## Installation

### 1. Install FFmpeg

```bash
brew install ffmpeg
```

### 2. Install the package

```bash
# Clone the repository
git clone <repository-url>
cd recording

# Install with Poetry
poetry install
```

### 3. (Optional) Install BlackHole for system audio recording

See [BlackHole Setup Guide](docs/blackhole_setup.md) for detailed instructions.

## Usage

### List available audio devices

```bash
poetry run mp3recorder list-devices
```

### Record audio

```bash
# Record for 10 seconds from default device
poetry run mp3recorder record --duration 10 --output my_recording.mp3

# Record from specific device (e.g., BlackHole)
poetry run mp3recorder record --duration 30 --device "BlackHole" --output output.mp3

# Record with custom bitrate
poetry run mp3recorder record --duration 60 --output hq.mp3 --bitrate 320
```

### Run as module

```bash
poetry run python -m mp3recorder list-devices
poetry run python -m mp3recorder record --duration 5 --output test.mp3
```

## Development

### Run tests

```bash
poetry run pytest
```

### Run tests with coverage

```bash
poetry run pytest --cov=mp3recorder --cov-report=term-missing
```

### Run linting

```bash
# Check for issues
poetry run ruff check src/ tests/

# Auto-fix issues
poetry run ruff check --fix src/ tests/

# Format code
poetry run ruff format src/ tests/
```

## Documentation

- [BlackHole Setup Guide](docs/blackhole_setup.md)
- [Usage Guide](docs/usage.md)

## License

MIT
