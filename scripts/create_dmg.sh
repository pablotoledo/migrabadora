#!/bin/bash
# Create DMG installer for MP3 Recorder
# Uses native hdiutil (no external dependencies)

set -e

APP_NAME="MP3 Recorder"
DMG_NAME="${APP_NAME}.dmg"
VOLUME_NAME="${APP_NAME}"

echo "📀 Creating DMG installer..."

# Check for app bundle
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "❌ Error: App bundle not found at dist/${APP_NAME}.app"
    echo "   Run 'make build-app' first"
    exit 1
fi

# Remove existing DMG
rm -f "dist/${DMG_NAME}"

# Create temporary DMG directory
TEMP_DIR=$(mktemp -d)
cp -R "dist/${APP_NAME}.app" "${TEMP_DIR}/"

# Create symbolic link to Applications
ln -s /Applications "${TEMP_DIR}/Applications"

# Create DMG using hdiutil
hdiutil create -volname "${VOLUME_NAME}" \
    -srcfolder "${TEMP_DIR}" \
    -ov -format UDZO \
    "dist/${DMG_NAME}"

# Cleanup
rm -rf "${TEMP_DIR}"

if [ -f "dist/${DMG_NAME}" ]; then
    echo ""
    echo "✅ DMG created: dist/${DMG_NAME}"
    echo ""
    echo "File size: $(du -h "dist/${DMG_NAME}" | cut -f1)"
else
    echo ""
    echo "❌ DMG creation failed"
    exit 1
fi
