#!/usr/bin/env python3
"""Real-time clock wallpaper — Linux & Windows. Jakarta timezone (WIB)."""

import os
import sys
import time
import json
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

DEFAULT_CONFIG = {
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
    "screen_height": 0,
}

ID_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
ID_MONTHS = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

RESAMPLING_NEAREST = getattr(getattr(Image, "Resampling", Image), "NEAREST")


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


def draw_centered(draw, x, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((x - w // 2, y), text, font=font, fill=fill)
    return h


def render_frame(cfg, base_img, now, fonts):
    img = base_img.copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size

    time_str = now.strftime(cfg["time_format"])
    date_str = format_date(now)
    tz_str = "WIB"

    font_clock, font_date, font_tz = fonts

    # Measure total block height for centering
    def text_h(text, font):
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[3] - bb[1]

    gap1, gap2 = 18, 10
    total_h = text_h(time_str, font_clock) + gap1 + text_h(date_str, font_date) + gap2 + text_h(tz_str, font_tz)

    pos = cfg.get("position", "center")
    padding = 60

    def block_x():
        if "right" in pos:
            return w - padding - max(
                draw.textbbox((0, 0), time_str, font=font_clock)[2],
                draw.textbbox((0, 0), date_str, font=font_date)[2],
                draw.textbbox((0, 0), tz_str, font=font_tz)[2],
            ) // 2
        if "left" in pos:
            return padding + max(
                draw.textbbox((0, 0), time_str, font=font_clock)[2],
                draw.textbbox((0, 0), date_str, font=font_date)[2],
                draw.textbbox((0, 0), tz_str, font=font_tz)[2],
            ) // 2
        return w // 2

    def block_y():
        if "top" in pos:
            return padding
        if "bottom" in pos:
            return h - total_h - padding
        return h // 2 - total_h // 2

    cx = block_x()
    y = block_y()

    y += draw_centered(draw, cx, y, time_str, font_clock, cfg["time_color"]) + gap1
    y += draw_centered(draw, cx, y, date_str, font_date, cfg["date_color"]) + gap2
    draw_centered(draw, cx, y, tz_str, font_tz, cfg["tz_color"])

    return img


def set_wallpaper(path: str, system: str):
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
                out = subprocess.check_output(["xrandr", "--listmonitors"], stderr=subprocess.DEVNULL).decode()
                monitors = re.findall(r"\d+: [+*]?(\S+)", out)
                for m in monitors:
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
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)


def main():
    cfg = load_config()
    system = platform.system()
    tz = ZoneInfo(cfg["timezone"])
    width, height = get_screen_size(cfg)

    fonts = (
        find_font(cfg["clock_font_size"], bold=True),
        find_font(cfg["date_font_size"]),
        find_font(cfg["tz_font_size"]),
    )

    # Pre-render gradient background (reuse every frame)
    base = make_gradient(width, height, cfg["background_top"], cfg["background_bottom"])

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False, prefix="clock_wp_")
    tmp_path = tmp.name
    tmp.close()

    print(f"Clock wallpaper running | {width}x{height} | {cfg['timezone']}")
    print(f"Temp: {tmp_path} | Ctrl+C to stop")

    try:
        while True:
            now = datetime.now(tz)
            img = render_frame(cfg, base, now, fonts)
            img.save(tmp_path, "PNG", compress_level=1)
            set_wallpaper(tmp_path, system)

            # Sleep until next whole second
            elapsed_us = datetime.now(tz).microsecond
            time.sleep(max(0, (1_000_000 - elapsed_us) / 1_000_000))
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


if __name__ == "__main__":
    main()
