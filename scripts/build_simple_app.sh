#!/bin/bash
#
# Simple macOS .app bundle builder for MP3 Recorder
# Creates a lightweight wrapper that calls the Python script
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

# Get Python path from Poetry
PYTHON_PATH=$(poetry env info --executable)
POETRY_PATH=$(which poetry)
PROJECT_DIR=$(pwd)

# Create the launcher script
cat > "${MACOS_DIR}/MP3 Recorder" << EOF
#!/bin/bash
# MP3 Recorder launcher
cd "${PROJECT_DIR}"
exec "${POETRY_PATH}" run mp3recorder-menubar
EOF

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
    # Add icon to plist
    /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string icon" "${CONTENTS_DIR}/Info.plist" 2>/dev/null || true
fi

echo "✅ Created ${APP_DIR}"
echo ""
echo "To install:"
echo "  cp -r '${APP_DIR}' /Applications/"
echo ""
echo "To run:"
echo "  open '${APP_DIR}'"
