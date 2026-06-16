#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(which python3)"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/clock-wallpaper.service"

echo "=== Clock Wallpaper Installer (Linux) ==="

# Install Pillow if missing
if ! "$PYTHON" -c "import PIL" 2>/dev/null; then
    echo "Installing Pillow..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
fi

# Create systemd user service
mkdir -p "$SERVICE_DIR"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Real-time Clock Wallpaper (Jakarta/WIB)
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart=$PYTHON $SCRIPT_DIR/clock_wallpaper.py
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
