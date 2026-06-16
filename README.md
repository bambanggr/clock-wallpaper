# Clock Wallpaper

Real-time clock wallpaper showing current time and date in **Jakarta (WIB / UTC+7)**.

```
         14:35:22

  Senin, 16 Juni 2026
         WIB
```

**Resource usage:** ~30–50 MB RAM, <0.5% CPU.

---

## Requirements

- Python 3.9+
- [Pillow](https://python-pillow.org/) (`pip install pillow`)

---

## Installation

### Linux

```bash
git clone https://github.com/bambanggr/clock-wallpaper.git
cd clock-wallpaper
bash install_linux.sh
```

The installer creates a **systemd user service** that starts automatically on login.

**Supported desktop environments:** GNOME, XFCE, KDE Plasma, MATE, Cinnamon, LXDE/LXQt, and any DE with `feh` installed.

**Useful commands after install:**

```bash
# Check status
systemctl --user status clock-wallpaper

# Stop
systemctl --user stop clock-wallpaper

# Restart (after config change)
systemctl --user restart clock-wallpaper

# View logs
journalctl --user -u clock-wallpaper -f
```

---

### Windows

```bat
git clone https://github.com/bambanggr/clock-wallpaper.git
cd clock-wallpaper
install_windows.bat
```

The installer copies a launcher to the **Startup folder** so it runs automatically on login.

**To start immediately (without rebooting):**

```bat
wscript start_wallpaper.vbs
```

**To stop:** Open Task Manager → find `pythonw.exe` → End Task.

---

### Manual (without installer)

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 clock_wallpaper.py
```

---

## Configuration

Edit `config.json` to customize appearance:

```json
{
    "timezone": "Asia/Jakarta",
    "time_format": "%H:%M:%S",
    "background_top": "#0f0c29",
    "background_bottom": "#302b63",
    "time_color": "#ffffff",
    "date_color": "#b0b0cc",
    "tz_color": "#6060aa",
    "position": "center",
    "clock_font_size": 120,
    "date_font_size": 42,
    "tz_font_size": 28,
    "screen_width": 0,
    "screen_height": 0
}
```

| Key | Description | Default |
|-----|-------------|---------|
| `timezone` | Any valid IANA timezone | `Asia/Jakarta` |
| `time_format` | `strftime` format string | `%H:%M:%S` |
| `background_top` | Gradient top color (hex) | `#0f0c29` |
| `background_bottom` | Gradient bottom color (hex) | `#302b63` |
| `time_color` | Clock text color (hex) | `#ffffff` |
| `date_color` | Date text color (hex) | `#b0b0cc` |
| `tz_color` | Timezone label color (hex) | `#6060aa` |
| `position` | `center`, `bottom-right`, `bottom-left`, `top-right`, `top-left` | `center` |
| `clock_font_size` | Clock font size in px | `120` |
| `date_font_size` | Date font size in px | `42` |
| `tz_font_size` | Timezone label font size in px | `28` |
| `screen_width` | Override screen width (0 = auto-detect) | `0` |
| `screen_height` | Override screen height (0 = auto-detect) | `0` |

After editing `config.json`, restart the service:

```bash
# Linux
systemctl --user restart clock-wallpaper

# Windows — kill pythonw.exe in Task Manager, then:
wscript start_wallpaper.vbs
```

---

## Custom Font

Drop your `.ttf` font files into the `assets/` folder:

- `assets/font.ttf` — regular
- `assets/font-bold.ttf` — bold (used for clock)

The script uses bundled fonts if present; otherwise falls back to system fonts.

---

## Uninstall

### Linux

```bash
systemctl --user stop clock-wallpaper
systemctl --user disable clock-wallpaper
rm ~/.config/systemd/user/clock-wallpaper.service
systemctl --user daemon-reload
```

### Windows

Delete `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\clock_wallpaper.vbs`.

---

## License

MIT
