#!/bin/bash
# Build script for macOS executable

echo "=========================================="
echo "Forenstiq Evidence Analyzer - macOS Build"
echo "=========================================="
echo ""

# Activate virtual environment
source venv/bin/activate

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist "Forenstiq Evidence Analyzer.app"

# Build the executable
echo ""
echo "Building macOS application..."
pyinstaller --clean --noconfirm forenstiq.spec

# Check if build was successful
if [ -d "dist/Forenstiq Evidence Analyzer.app" ]; then
    echo ""
    echo "=========================================="
    echo "✓ Build successful!"
    echo "=========================================="
    echo ""
    echo "Application location:"
    echo "  dist/Forenstiq Evidence Analyzer.app"
    echo ""
    echo "To distribute:"
    echo "  1. Copy 'dist/Forenstiq Evidence Analyzer.app' to any Mac"
    echo "  2. Double-click to run"
    echo ""
    echo "To create a DMG for distribution:"
    echo "  hdiutil create -volname 'Forenstiq Evidence Analyzer' -srcfolder 'dist/Forenstiq Evidence Analyzer.app' -ov -format UDZO Forenstiq-macOS.dmg"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "✗ Build failed!"
    echo "=========================================="
    echo "Check the output above for errors."
    exit 1
fi
