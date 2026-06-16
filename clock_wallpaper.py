#!/usr/bin/env python3
"""Real-time clock wallpaper — Linux & Windows. Jakarta timezone (WIB)."""

import os
import sys
import time
import json
import logging
import platform
import subprocess
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = SCRIPT_DIR / "config.json"
ASSETS_DIR = SCRIPT_DIR / "assets"
LOG_FILE = SCRIPT_DIR / "clock_wallpaper.log"

DEFAULT_CONFIG = {
    "timezone": "Asia/Jakarta",
    "time_format": "%H:%M",
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
    "screen_height": 0,
}

ID_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
ID_MONTHS = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

RESAMPLING_NEAREST = getattr(getattr(Image, "Resampling", Image), "NEAREST")


def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    handlers = [logging.StreamHandler()]
    # Always log to file when running without terminal (e.g. pythonw on Windows)
    if not sys.stdout or not sys.stdout.isatty():
        handlers = [logging.FileHandler(LOG_FILE)]
    elif debug:
        handlers.append(logging.FileHandler(LOG_FILE))
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()


def find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    suffix = "-bold" if bold else ""
    bundled = ASSETS_DIR / f"font{suffix}.ttf"
    if bundled.exists():
        return ImageFont.truetype(str(bundled), size)

    system = platform.system()
    if system == "Linux":
        candidates = [
            f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
            f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
            f"/usr/share/fonts/truetype/ubuntu/Ubuntu-{'B' if bold else 'R'}.ttf",
            f"/usr/share/fonts/TTF/DejaVuSans{'-Bold' if bold else ''}.ttf",
            f"/usr/share/fonts/truetype/freefont/FreeSans{'Bold' if bold else ''}.ttf",
        ]
    elif system == "Windows":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        candidates = [
            fr"{windir}\Fonts\{'arialbd' if bold else 'arial'}.ttf",
            fr"{windir}\Fonts\{'calibrib' if bold else 'calibri'}.ttf",
            fr"{windir}\Fonts\{'segoeuib' if bold else 'segoeui'}.ttf",
        ]
    else:
        candidates = []

    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def hex_to_rgb(color: str) -> tuple:
    h = color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def make_gradient(width: int, height: int, top: str, bottom: str) -> Image.Image:
    r1, g1, b1 = hex_to_rgb(top)
    r2, g2, b2 = hex_to_rgb(bottom)
    col = Image.new("RGB", (1, height))
    draw = ImageDraw.Draw(col)
    for y in range(height):
        t = y / max(height - 1, 1)
        draw.point(
            (0, y),
            fill=(
                int(r1 + (r2 - r1) * t),
                int(g1 + (g2 - g1) * t),
                int(b1 + (b2 - b1) * t),
            ),
        )
    return col.resize((width, height), RESAMPLING_NEAREST)


def get_screen_size(cfg: dict) -> tuple:
    if cfg["screen_width"] and cfg["screen_height"]:
        return cfg["screen_width"], cfg["screen_height"]

    system = platform.system()
    if system == "Linux":
        try:
            import re
            out = subprocess.check_output(["xrandr"], stderr=subprocess.DEVNULL).decode()
            for line in out.splitlines():
                if " connected" in line:
                    m = re.search(r"(\d+)x(\d+)\+", line)
                    if m:
                        return int(m.group(1)), int(m.group(2))
        except Exception:
            pass
    elif system == "Windows":
        try:
            import ctypes
            u32 = ctypes.windll.user32
            return u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)
        except Exception:
            pass

    return 1920, 1080


def format_date(dt: datetime) -> str:
    return f"{ID_DAYS[dt.weekday()]}, {dt.day} {ID_MONTHS[dt.month]} {dt.year}"


def render_frame(cfg, base_img, now, fonts):
    img = base_img.copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size

    time_str = now.strftime(cfg["time_format"])
    date_str = format_date(now)
    tz_str = "WIB"
    font_clock, font_date, font_tz = fonts

    def measure(text, font):
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0], bb[3] - bb[1]

    tw, th = measure(time_str, font_clock)
    dw, dh = measure(date_str, font_date)
    zw, zh = measure(tz_str, font_tz)

    gap1, gap2 = 18, 10
    total_h = th + gap1 + dh + gap2 + zh
    max_w = max(tw, dw, zw)

    pos = cfg.get("position", "center")
    padding = 60

    if pos == "center":
        cx, cy = w // 2, h // 2 - total_h // 2
    elif pos == "bottom-right":
        cx, cy = w - max_w // 2 - padding, h - total_h - padding
    elif pos == "bottom-left":
        cx, cy = max_w // 2 + padding, h - total_h - padding
    elif pos == "top-right":
        cx, cy = w - max_w // 2 - padding, padding
    elif pos == "top-left":
        cx, cy = max_w // 2 + padding, padding
    else:
        cx, cy = w // 2, h // 2 - total_h // 2

    def put(y, text, font, fill):
        _, th = measure(text, font)
        tw, _ = measure(text, font)
        draw.text((cx - tw // 2, y), text, font=font, fill=fill)
        return th

    y = cy
    y += put(y, time_str, font_clock, cfg["time_color"]) + gap1
    y += put(y, date_str, font_date, cfg["date_color"]) + gap2
    put(y, tz_str, font_tz, cfg["tz_color"])

    return img


def run_overlay(cfg, tz, width, height, fonts, base):
    """
    Tkinter canvas overlay — zero flicker.
    Linux X11/XWayland: window type 'desktop' keeps it behind all apps.
    Windows: HWND_BOTTOM keeps it at lowest z-order.
    """
    try:
        import tkinter as tk
        from PIL import ImageTk
    except ImportError as e:
        logging.error("tkinter unavailable: %s — falling back to wallpaper mode", e)
        run_wallpaper(cfg, tz, width, height, fonts, base)
        return

    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f"{width}x{height}+0+0")
    root.configure(bg="black")

    system = platform.system()
    if system == "Linux":
        # Works on X11 and XWayland — GNOME/XFCE/KDE respect _NET_WM_WINDOW_TYPE_DESKTOP
        root.attributes("-type", "desktop")
        root.lower()
    elif system == "Windows":
        root.update_idletasks()
        try:
            import ctypes
            hwnd = root.winfo_id()
            HWND_BOTTOM = 1
            SWP_NOSIZE_NOMOVE = 0x0001 | 0x0002
            ctypes.windll.user32.SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0, SWP_NOSIZE_NOMOVE)
        except Exception as e:
            logging.warning("SetWindowPos failed: %s", e)

    canvas = tk.Canvas(root, width=width, height=height, highlightthickness=0, bd=0)
    canvas.pack(fill="both", expand=True)

    # Create initial frame
    now = datetime.now(tz)
    photo = ImageTk.PhotoImage(render_frame(cfg, base, now, fonts))
    img_id = canvas.create_image(0, 0, image=photo, anchor="nw")
    # holder[0] = current photo (keeps ref alive), holder[1] = last display key
    holder = [photo, ""]

    def display_key(dt):
        return dt.strftime(cfg["time_format"]) + format_date(dt)

    def ms_until_next_tick(dt):
        """Sleep until next second; if no seconds in format, sleep to next minute."""
        if "%S" in cfg["time_format"]:
            return max(50, 1000 - dt.microsecond // 1000)
        return max(50, (60 - dt.second) * 1000 - dt.microsecond // 1000)

    def tick():
        now = datetime.now(tz)
        key = display_key(now)
        if key != holder[1]:
            new_photo = ImageTk.PhotoImage(render_frame(cfg, base, now, fonts))
            canvas.itemconfig(img_id, image=new_photo)
            holder[0] = new_photo
            holder[1] = key
        root.after(ms_until_next_tick(datetime.now(tz)), tick)

    root.after(ms_until_next_tick(datetime.now(tz)), tick)

    logging.info("Overlay mode started — %dx%d — %s", width, height, cfg["timezone"])
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


def set_wallpaper(path: str, system: str):
    logging.debug("Setting wallpaper: %s", path)
    if system == "Linux":
        de = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        session = os.environ.get("DESKTOP_SESSION", "").lower()

        if any(k in de for k in ("gnome", "unity", "budgie", "pantheon")):
            uri = f"file://{path}"
            subprocess.run(
                ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri],
                capture_output=True,
            )
            subprocess.run(
                ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri],
                capture_output=True,
            )
        elif any(k in de + session for k in ("xfce",)):
            try:
                import re
                out = subprocess.check_output(
                    ["xrandr", "--listmonitors"], stderr=subprocess.DEVNULL
                ).decode()
                for m in re.findall(r"\d+: [+*]?(\S+)", out):
                    subprocess.run(
                        ["xfconf-query", "-c", "xfce4-desktop", "-p",
                         f"/backdrop/screen0/monitor{m}/workspace0/last-image", "-s", path],
                        capture_output=True,
                    )
            except Exception:
                subprocess.run(["feh", "--bg-fill", path], capture_output=True)
        elif any(k in de for k in ("kde", "plasma")):
            script = (
                "var d=desktops();"
                "for(var i=0;i<d.length;i++){"
                "d[i].wallpaperPlugin='org.kde.image';"
                "d[i].currentConfigGroup=Array('Wallpaper','org.kde.image','General');"
                f"d[i].writeConfig('Image','file://{path}');}}"
            )
            subprocess.run(
                ["qdbus", "org.kde.plasmashell", "/PlasmaShell",
                 "org.kde.PlasmaShell.evaluateScript", script],
                capture_output=True,
            )
        elif "mate" in de:
            subprocess.run(
                ["gsettings", "set", "org.mate.background", "picture-filename", path],
                capture_output=True,
            )
        elif "cinnamon" in de:
            subprocess.run(
                ["gsettings", "set", "org.cinnamon.desktop.background",
                 "picture-uri", f"file://{path}"],
                capture_output=True,
            )
        elif "lxde" in de or "lxqt" in de:
            subprocess.run(["pcmanfm", "--set-wallpaper", path], capture_output=True)
        else:
            subprocess.run(["feh", "--bg-fill", path], capture_output=True)

    elif system == "Windows":
        import ctypes
        result = ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
        if not result:
            logging.error("SystemParametersInfoW failed (path=%s)", path)
        else:
            logging.debug("Wallpaper set OK")


def run_wallpaper(cfg, tz, width, height, fonts, base):
    """File-based wallpaper mode. Use --wallpaper flag or on pure Wayland."""
    system = platform.system()
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False, prefix="clock_wp_")
    tmp_path = os.path.abspath(tmp.name)
    tmp.close()

    logging.info("Wallpaper mode started — %dx%d — %s", width, height, cfg["timezone"])
    logging.info("Temp file: %s", tmp_path)

    has_seconds = "%S" in cfg["time_format"]
    prev_key = ""

    try:
        while True:
            now = datetime.now(tz)
            key = now.strftime(cfg["time_format"]) + format_date(now)
            if key != prev_key:
                render_frame(cfg, base, now, fonts).save(tmp_path, "PNG", compress_level=1)
                set_wallpaper(tmp_path, system)
                prev_key = key

            if has_seconds:
                elapsed_us = datetime.now(tz).microsecond
                time.sleep(max(0, (1_000_000 - elapsed_us) / 1_000_000))
            else:
                now = datetime.now(tz)
                time.sleep(max(0, 60 - now.second - now.microsecond / 1_000_000))
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def detect_mode(force: str | None) -> str:
    """Return 'overlay' or 'wallpaper'."""
    if force:
        return force
    system = platform.system()
    if system == "Windows":
        return "overlay"
    # Linux: use overlay if any X display is available (X11 or XWayland)
    if os.environ.get("DISPLAY"):
        return "overlay"
    return "wallpaper"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Real-time clock wallpaper")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--overlay", action="store_true", help="Force tkinter overlay mode (default on X11/Windows)")
    group.add_argument("--wallpaper", action="store_true", help="Force file-based wallpaper mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging to clock_wallpaper.log")
    args = parser.parse_args()

    force = "overlay" if args.overlay else ("wallpaper" if args.wallpaper else None)
    setup_logging(args.debug)

    cfg = load_config()
    tz = ZoneInfo(cfg["timezone"])
    width, height = get_screen_size(cfg)

    fonts = (
        find_font(cfg["clock_font_size"], bold=True),
        find_font(cfg["date_font_size"]),
        find_font(cfg["tz_font_size"]),
    )
    base = make_gradient(width, height, cfg["background_top"], cfg["background_bottom"])

    mode = detect_mode(force)
    logging.info("Mode: %s | %dx%d | %s", mode, width, height, cfg["timezone"])
    print(f"Clock wallpaper | mode={mode} | {width}x{height} | {cfg['timezone']} | Ctrl+C to stop")

    if mode == "overlay":
        run_overlay(cfg, tz, width, height, fonts, base)
    else:
        run_wallpaper(cfg, tz, width, height, fonts, base)


if __name__ == "__main__":
    main()
