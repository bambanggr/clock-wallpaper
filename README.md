# Clock Wallpaper

Real-time clock wallpaper showing current time and date in **Jakarta (WIB / UTC+7)**.

```
         14:35

  Senin, 16 Juni 2026
         WIB
```

**Resource usage:** ~30–50 MB RAM, <0.5% CPU.

Runs as the actual desktop background image (not a window), so it never blocks
clicks to desktop icons or other apps. Updates once a minute (or every second
if you enable `%S` in the time format).

---

## Quick start (no terminal, no Python required)

1. Download `ClockWallpaper.exe` (Windows) or `ClockWallpaper` (Linux) from the
   project's [Releases page](https://github.com/bambanggr/clock-wallpaper/releases) —
   or build it yourself, see [Building the executable](#building-the-executable) below.
2. Double-click it. A small window opens with **Start**, **Stop**, and
   **Enable/Disable autostart** buttons.
3. Click **Install / Update** once — this sets up autostart and starts the
   clock immediately. From then on, use Start/Stop as needed.

That's it — no Python, no venv, no terminal. This is the same `manage.py` GUI
on both platforms, so Windows and Linux work identically once you have the
executable.

> Linux note: on first run you may need `chmod +x ClockWallpaper` and, if
> double-click doesn't open it, `sudo apt install python3-tk` is **not**
> needed for the prebuilt binary (it's bundled in) — that's only required if
> you build/run from source.

---

## Building the executable

You need [Python 3.9+](https://python.org) once, just to build. End users of
the resulting file don't need Python at all.

**Windows:**

```bat
build_windows.bat
```

Produces `dist\ClockWallpaper.exe` — copy that single file anywhere.

**Linux:**

```bash
sudo apt install python3-tk   # if not already installed
./build_linux.sh
```

Produces `dist/ClockWallpaper` — copy that single file anywhere, `chmod +x` it.

**Automated builds (both platforms at once):** push a tag like `v1.0.0` and
GitHub Actions (`.github/workflows/build.yml`) builds both the Windows `.exe`
and the Linux binary and attaches them to a GitHub Release automatically.
You can also trigger it manually from the Actions tab (`workflow_dispatch`)
without tagging, and grab the build from the run's Artifacts.

---

## Running from source (developers)

```bash
git clone https://github.com/bambanggr/clock-wallpaper.git
cd clock-wallpaper
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 manage.py                # GUI manager
# or
python3 clock_wallpaper.py       # run the clock directly, Ctrl+C to stop
```

Double-click launchers are also available without opening a terminal:
`manage.sh` (Linux) and `Manage Clock Wallpaper.vbs` (Windows) — both run
`manage.py` using the local `.venv` if present.

The old terminal-only installers (`install_linux.sh`, `install_windows.bat`)
still work and set up the same systemd service / Startup-folder entry as the
GUI manager's Install button, if you prefer scripting an install.

---

## Configuration

Edit `config.json` to customize appearance (next to the executable, or in
the project folder when running from source):

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
| `time_format` | `strftime` format string — `%H:%M` (no seconds) or `%H:%M:%S` | `%H:%M` |
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

After editing `config.json`, restart via the GUI manager (**Stop** then
**Start**), or:

```bash
# Linux
systemctl --user restart clock-wallpaper

# Windows
# Use the manager's Stop then Start button (simplest), or end
# ClockWallpaper.exe in Task Manager, then click Start again.
```

---

## Advanced: overlay mode

By default the clock renders as the actual desktop wallpaper image (most
reliable across DEs and Windows DPI setups). A tkinter-window-based overlay
mode also exists for advanced use, but it can mis-size on scaled displays or
block clicks to desktop icons depending on your desktop environment/Windows
version — most people don't need it:

```bash
python3 clock_wallpaper.py --overlay
```

---

## Custom Font

Drop your `.ttf` font files into the `assets/` folder next to the script (or
next to the executable, if frozen):

- `assets/font.ttf` — regular
- `assets/font-bold.ttf` — bold (used for clock)

The script uses bundled fonts if present; otherwise falls back to system fonts.

---

## Uninstall

Easiest: open the GUI manager, click **Stop**, then **Disable** autostart.

To fully remove the systemd service / Startup entry by hand:

### Linux

```bash
systemctl --user stop clock-wallpaper
systemctl --user disable clock-wallpaper
rm ~/.config/systemd/user/clock-wallpaper.service
systemctl --user daemon-reload
rm -f ~/.local/share/applications/clock-wallpaper.desktop ~/Desktop/"Clock Wallpaper.desktop"
```

### Windows

Delete `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\clock_wallpaper.vbs`.

---

## License

MIT
