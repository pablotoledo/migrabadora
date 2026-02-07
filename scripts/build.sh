#!/bin/bash
# MP3 Recorder Build Script
# Builds the macOS app bundle using py2app

set -e

echo "🎙️ MP3 Recorder Build Script"
echo "============================"
echo ""

# Check we're in the right directory
if [ ! -f "setup_app.py" ]; then
    echo "❌ Error: Must be run from project root directory"
    exit 1
fi

# Check for py2app
if ! poetry run python -c "import py2app" 2>/dev/null; then
    echo "📦 Installing py2app..."
    poetry add --group dev py2app
fi

# Check for icon file
if [ ! -f "resources/icon.icns" ]; then
    echo "⚠️  Warning: No icon file found at resources/icon.icns"
    echo "   The app will use a default icon."
    echo ""
    # Create a placeholder to avoid build errors
    # In production, you'd want a real icon
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Build the app
echo "📦 Building app bundle..."
poetry run python setup_app.py py2app

# Verify the build
if [ -d "dist/MP3 Recorder.app" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "Application: dist/MP3 Recorder.app"
    echo ""
    echo "To install:"
    echo "  cp -r 'dist/MP3 Recorder.app' /Applications/"
    echo ""
    echo "To run:"
    echo "  open 'dist/MP3 Recorder.app'"
else
    echo ""
    echo "❌ Build failed!"
    exit 1
fi
