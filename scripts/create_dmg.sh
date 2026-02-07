#!/bin/bash
# Create DMG installer for MP3 Recorder
# Requires: create-dmg (brew install create-dmg)

set -e

echo "📀 Creating DMG installer..."

# Check for create-dmg
if ! command -v create-dmg &> /dev/null; then
    echo "❌ Error: create-dmg not found"
    echo "   Install with: brew install create-dmg"
    exit 1
fi

# Check for app bundle
if [ ! -d "dist/MP3 Recorder.app" ]; then
    echo "❌ Error: App bundle not found at dist/MP3 Recorder.app"
    echo "   Run 'make build-app' first"
    exit 1
fi

# Remove existing DMG
rm -f "dist/MP3 Recorder.dmg"

# Create DMG
create-dmg \
    --volname "MP3 Recorder" \
    --volicon "resources/icon.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "MP3 Recorder.app" 150 190 \
    --hide-extension "MP3 Recorder.app" \
    --app-drop-link 450 190 \
    "dist/MP3 Recorder.dmg" \
    "dist/MP3 Recorder.app" \
    || true  # create-dmg returns non-zero even on success sometimes

if [ -f "dist/MP3 Recorder.dmg" ]; then
    echo ""
    echo "✅ DMG created: dist/MP3 Recorder.dmg"
    echo ""
    echo "File size: $(du -h 'dist/MP3 Recorder.dmg' | cut -f1)"
else
    echo ""
    echo "❌ DMG creation failed"
    exit 1
fi
