#!/bin/bash
# MP3 Recorder Uninstall Script
# Removes all MP3 Recorder data from your Mac

set -e

echo "🎙️ MP3 Recorder Uninstaller"
echo "=========================="
echo ""

# Define paths
LAUNCH_AGENT="$HOME/Library/LaunchAgents/com.mp3recorder.menubar.plist"
CONFIG_DIR="$HOME/Library/Application Support/MP3Recorder"
LOG_DIR="$HOME/Library/Logs/MP3Recorder"
APP_PATH="/Applications/MP3 Recorder.app"

# Show what will be removed
echo "The following will be removed (if they exist):"
echo ""

if [ -f "$LAUNCH_AGENT" ]; then
    echo "  ✓ LaunchAgent: $LAUNCH_AGENT"
fi

if [ -d "$CONFIG_DIR" ]; then
    echo "  ✓ Configuration: $CONFIG_DIR"
fi

if [ -d "$LOG_DIR" ]; then
    echo "  ✓ Logs: $LOG_DIR"
fi

if [ -d "$APP_PATH" ]; then
    echo "  ✓ Application: $APP_PATH"
fi

echo ""
read -p "Are you sure you want to continue? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Uninstalling..."

# Unload and remove LaunchAgent
if [ -f "$LAUNCH_AGENT" ]; then
    echo "Removing LaunchAgent..."
    launchctl unload "$LAUNCH_AGENT" 2>/dev/null || true
    rm -f "$LAUNCH_AGENT"
    echo "  ✓ Done"
fi

# Remove config directory
if [ -d "$CONFIG_DIR" ]; then
    echo "Removing configuration..."
    rm -rf "$CONFIG_DIR"
    echo "  ✓ Done"
fi

# Remove logs directory
if [ -d "$LOG_DIR" ]; then
    echo "Removing logs..."
    rm -rf "$LOG_DIR"
    echo "  ✓ Done"
fi

# Remove app bundle
if [ -d "$APP_PATH" ]; then
    echo "Removing application..."
    rm -rf "$APP_PATH"
    echo "  ✓ Done"
fi

echo ""
echo "✅ MP3 Recorder has been completely removed from your Mac."
echo ""
echo "Thank you for using MP3 Recorder!"
