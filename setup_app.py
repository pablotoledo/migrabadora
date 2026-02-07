"""
py2app build configuration for MP3 Recorder.

This script configures the build process for creating a native macOS application
bundle (.app) for MP3 Recorder.

Usage:
    python setup_app.py py2app

Or using the build script:
    make build-app
"""

from setuptools import setup

APP = ["src/mp3recorder/menubar.py"]
DATA_FILES: list = []

OPTIONS = {
    "argv_emulation": False,
    "iconfile": "resources/icon.icns",
    "plist": {
        "CFBundleName": "MP3 Recorder",
        "CFBundleDisplayName": "MP3 Recorder",
        "CFBundleIdentifier": "com.mp3recorder.menubar",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "CFBundleDevelopmentRegion": "en",
        "NSHumanReadableCopyright": "Copyright © 2024 MP3 Recorder",
        "NSHighResolutionCapable": True,
        # This makes it a menu bar only app (no Dock icon)
        "LSUIElement": True,
        # Required for audio recording
        "NSMicrophoneUsageDescription": "MP3 Recorder needs access to the microphone to record audio.",
        # For notifications
        "NSUserNotificationAlertStyle": "alert",
    },
    "packages": [
        "mp3recorder",
        "sounddevice",
        "numpy",
        "pydub",
        "rumps",
    ],
    # Include these packages in the app bundle
    "includes": [
        "mp3recorder",
        "mp3recorder.config",
        "mp3recorder.dependencies",
        "mp3recorder.devices",
        "mp3recorder.logging_config",
        "mp3recorder.menubar",
        "mp3recorder.recorder",
        "mp3recorder.startup",
    ],
    # Exclude unnecessary modules to reduce bundle size
    "excludes": [
        "pytest",
        "pytest_cov",
        "ruff",
        "black",
        "mypy",
        "sphinx",
        "docutils",
    ],
}

setup(
    name="MP3 Recorder",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
