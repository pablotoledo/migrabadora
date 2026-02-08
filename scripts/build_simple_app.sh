#!/bin/bash
#
# Simple macOS .app bundle builder for MP3 Recorder
# Creates a lightweight wrapper that calls the Python script via terminal
#

set -e

APP_NAME="MP3 Recorder"
APP_DIR="dist/${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

echo "📦 Building ${APP_NAME}.app (simple wrapper)..."

# Clean previous build
rm -rf "dist/${APP_NAME}.app"

# Create directory structure
mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"

# Get paths
PROJECT_DIR=$(pwd)

# Create the launcher script
# Uses osascript to run shell command which avoids TCC restrictions
cat > "${MACOS_DIR}/MP3 Recorder" << 'LAUNCHER_EOF'
#!/bin/bash

# Project directory is stored during build
PROJECT_DIR="__PROJECT_DIR__"

# Log file
LOG_FILE="$HOME/Library/Logs/MP3Recorder/launcher.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log "Starting MP3 Recorder..."

cd "$PROJECT_DIR" 2>/dev/null || {
    log "ERROR: Project not found at $PROJECT_DIR"
    osascript -e 'display dialog "MP3 Recorder Error:\n\nProject directory not found:\n'"$PROJECT_DIR"'" buttons {"OK"} default button 1 with icon stop'
    exit 1
}

# Check if poetry is available  
if command -v /opt/homebrew/bin/poetry &> /dev/null; then
    POETRY_CMD="/opt/homebrew/bin/poetry"
elif command -v poetry &> /dev/null; then
    POETRY_CMD="poetry"
else
    log "ERROR: Poetry not found"
    osascript -e 'display dialog "MP3 Recorder Error:\n\nPoetry not found. Please install Poetry and try again." buttons {"OK"} default button 1 with icon stop'
    exit 1
fi

log "Using poetry: $POETRY_CMD"
log "Launching in background..."

# Run the app - using nohup to detach from terminal context
nohup "$POETRY_CMD" run mp3recorder-menubar >> "$LOG_FILE" 2>&1 &

log "App started with PID $!"
LAUNCHER_EOF

# Replace placeholders
sed -i '' "s|__PROJECT_DIR__|${PROJECT_DIR}|g" "${MACOS_DIR}/MP3 Recorder"

chmod +x "${MACOS_DIR}/MP3 Recorder"

# Create Info.plist
cat > "${CONTENTS_DIR}/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>MP3 Recorder</string>
    <key>CFBundleDisplayName</key>
    <string>MP3 Recorder</string>
    <key>CFBundleIdentifier</key>
    <string>com.mp3recorder.menubar</string>
    <key>CFBundleVersion</key>
    <string>0.1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>0.1.0</string>
    <key>CFBundleExecutable</key>
    <string>MP3 Recorder</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSMicrophoneUsageDescription</key>
    <string>MP3 Recorder needs access to the microphone to record audio.</string>
</dict>
</plist>
EOF

# Copy icon if exists
if [ -f "resources/icon.icns" ]; then
    cp "resources/icon.icns" "${RESOURCES_DIR}/icon.icns"
    /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string icon" "${CONTENTS_DIR}/Info.plist" 2>/dev/null || true
fi

echo "✅ Created ${APP_DIR}"
echo ""
echo "To install:"
echo "  cp -r '${APP_DIR}' /Applications/"
echo ""
echo "To run:"
echo "  open '${APP_DIR}'"
echo ""
echo "Logs: ~/Library/Logs/MP3Recorder/launcher.log"
