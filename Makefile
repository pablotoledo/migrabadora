# MP3 Recorder Makefile
# Commands for development, testing, and building

.PHONY: all install dev test lint format clean build-app dmg help

# Default target
all: help

# Install dependencies
install:
	poetry install

# Run in development mode
dev:
	poetry run mp3recorder-menubar

# Run tests
test:
	poetry run pytest --cov=mp3recorder --cov-report=term-missing

# Run tests with verbose output
test-v:
	poetry run pytest -v --cov=mp3recorder --cov-report=term-missing

# Run linter
lint:
	poetry run ruff check src tests

# Format code
format:
	poetry run ruff format src tests
	poetry run ruff check --fix src tests

# Clean build artifacts
clean:
	rm -rf build dist
	rm -rf *.pyc __pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .coverage
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Build the macOS app bundle (simple wrapper)
build-app: clean
	@echo "📦 Building MP3 Recorder.app..."
	chmod +x scripts/build_simple_app.sh
	./scripts/build_simple_app.sh
	@echo "✅ Build complete: dist/MP3 Recorder.app"

# Build app with py2app (currently broken on macOS 26)
build-app-py2app: clean
	@echo "📦 Building MP3 Recorder.app with py2app..."
	@echo "⚠️  Note: py2app may fail on macOS 26"
	poetry run python setup_app.py py2app
	@echo "✅ Build complete: dist/MP3 Recorder.app"

# Create DMG installer
dmg: build-app
	@echo "📀 Creating DMG installer..."
	./scripts/create_dmg.sh
	@echo "✅ DMG complete: dist/MP3 Recorder.dmg"

# Quick build check (runs tests + lint)
check: lint test

# Full CI check
ci: lint test

# Show help
help:
	@echo "MP3 Recorder - Build Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install     - Install dependencies"
	@echo "  make dev         - Run the menu bar app"
	@echo "  make test        - Run tests with coverage"
	@echo "  make lint        - Run linter"
	@echo "  make format      - Format code"
	@echo ""
	@echo "Building:"
	@echo "  make build-app   - Build the macOS .app bundle"
	@echo "  make build-app-dev - Build app in alias mode (faster)"
	@echo "  make dmg         - Create DMG installer"
	@echo "  make clean       - Remove build artifacts"
	@echo ""
	@echo "CI:"
	@echo "  make check       - Run lint + test"
	@echo "  make ci          - Full CI check"
