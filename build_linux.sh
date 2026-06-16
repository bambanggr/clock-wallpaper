#!/usr/bin/env bash
# Build a standalone ClockWallpaper binary for Linux using PyInstaller.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Building ClockWallpaper binary ==="

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found. Install it first (e.g. sudo apt install python3)."
    exit 1
fi

if ! python3 -c "import tkinter" >/dev/null 2>&1; then
    echo "ERROR: tkinter not found. Install it first: sudo apt install python3-tk"
    exit 1
fi

echo "Installing build dependencies..."
python3 -m pip install --quiet --upgrade pip pyinstaller
python3 -m pip install --quiet -r "$SCRIPT_DIR/requirements.txt"

echo "Building single-file executable..."
python3 -m PyInstaller --onefile --name ClockWallpaper \
    --distpath "$SCRIPT_DIR/dist" \
    --workpath "$SCRIPT_DIR/build" \
    --specpath "$SCRIPT_DIR/build" \
    "$SCRIPT_DIR/manage.py"

echo
echo "Done! Executable: $SCRIPT_DIR/dist/ClockWallpaper"
echo "Copy that single file anywhere, 'chmod +x' it if needed, and double-click (or ./ClockWallpaper) to run."
