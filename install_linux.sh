#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON="$(which python3)"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/clock-wallpaper.service"

echo "=== Clock Wallpaper Installer (Linux) ==="

# Ensure venv module is available
if ! "$PYTHON" -m venv --help &>/dev/null; then
    echo "python3-venv not found, attempting to install..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3-venv
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3-venv
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm python-virtualenv
    else
        echo "Cannot install python3-venv automatically. Install it manually and re-run."
        exit 1
    fi
fi

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR ..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python3"

echo "Installing dependencies into venv..."
"$VENV_PYTHON" -m pip install --quiet --upgrade pip
"$VENV_PYTHON" -m pip install --quiet -r "$SCRIPT_DIR/requirements.txt"

# Create systemd user service
mkdir -p "$SERVICE_DIR"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Real-time Clock Wallpaper (Jakarta/WIB)
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart=$VENV_PYTHON $SCRIPT_DIR/clock_wallpaper.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical-session.target
EOF

echo "Service file created: $SERVICE_FILE"

systemctl --user daemon-reload
systemctl --user enable clock-wallpaper.service
systemctl --user start clock-wallpaper.service

echo ""
echo "Done! Clock wallpaper is running."
echo ""
echo "Useful commands:"
echo "  systemctl --user status clock-wallpaper"
echo "  systemctl --user stop clock-wallpaper"
echo "  systemctl --user restart clock-wallpaper"
echo "  journalctl --user -u clock-wallpaper -f"
