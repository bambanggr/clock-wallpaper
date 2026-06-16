#!/usr/bin/env python3
"""Clock Wallpaper Manager — double-click to open, no terminal needed."""

import os
import sys
import subprocess
import platform
import threading
import shutil
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    sys.exit("tkinter tidak ditemukan.\nUbuntu/Debian: sudo apt install python3-tk")

SCRIPT_DIR = Path(__file__).parent.resolve()
VENV_DIR   = SCRIPT_DIR / ".venv"
CLOCK_PY   = SCRIPT_DIR / "clock_wallpaper.py"
REQ_FILE   = SCRIPT_DIR / "requirements.txt"
SYSTEM     = platform.system()
PID_FILE   = SCRIPT_DIR / ".clock_pid"

if SYSTEM == "Linux":
    VENV_PY      = VENV_DIR / "bin" / "python3"
    PIP          = VENV_DIR / "bin" / "pip"
    SERVICE_DIR  = Path.home() / ".config" / "systemd" / "user"
    SERVICE_FILE = SERVICE_DIR / "clock-wallpaper.service"
elif SYSTEM == "Windows":
    VENV_PY     = VENV_DIR / "Scripts" / "pythonw.exe"
    PIP         = VENV_DIR / "Scripts" / "pip.exe"
    STARTUP_DIR = (
        Path(os.environ.get("APPDATA", ""))
        / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    )
    STARTUP_VBS = STARTUP_DIR / "clock_wallpaper.vbs"


def _run(*args) -> subprocess.CompletedProcess:
    return subprocess.run(list(args), capture_output=True, text=True)


# ── Windows: find running process by command line ─────────────────────────────

def _win_find_pid() -> str:
    if PID_FILE.exists():
        pid = PID_FILE.read_text().strip()
        r = _run("tasklist", "/FI", f"PID eq {pid}")
        if "pythonw" in r.stdout.lower():
            return pid
    ps = (
        "(Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe'\" |"
        " Where-Object CommandLine -like '*clock_wallpaper*').ProcessId"
    )
    r = _run("powershell", "-NoProfile", "-Command", ps)
    pid = r.stdout.strip()
    return pid if pid.isdigit() else ""


# ── status ────────────────────────────────────────────────────────────────────

def is_installed() -> bool:
    if not VENV_PY.exists():
        return False
    if SYSTEM == "Linux":
        return SERVICE_FILE.exists()
    return True


def is_running() -> bool:
    if SYSTEM == "Linux":
        r = _run("systemctl", "--user", "is-active", "clock-wallpaper")
        return r.stdout.strip() == "active"
    if SYSTEM == "Windows":
        return bool(_win_find_pid())
    return False


def is_autostart() -> bool:
    if SYSTEM == "Linux":
        r = _run("systemctl", "--user", "is-enabled", "clock-wallpaper")
        return r.stdout.strip() == "enabled"
    if SYSTEM == "Windows":
        return STARTUP_VBS.exists()
    return False


# ── control ───────────────────────────────────────────────────────────────────

def do_start():
    if SYSTEM == "Linux":
        _run("systemctl", "--user", "start", "clock-wallpaper")
    elif SYSTEM == "Windows":
        pythonw = str(VENV_PY) if VENV_PY.exists() else (shutil.which("pythonw") or "python")
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        proc = subprocess.Popen([pythonw, str(CLOCK_PY)], creationflags=flags)
        try:
            PID_FILE.write_text(str(proc.pid))
        except OSError:
            pass


def do_stop():
    if SYSTEM == "Linux":
        _run("systemctl", "--user", "stop", "clock-wallpaper")
    elif SYSTEM == "Windows":
        pid = _win_find_pid()
        if pid:
            _run("taskkill", "/F", "/PID", pid)
            try:
                PID_FILE.unlink()
            except OSError:
                pass


def do_enable_auto():
    if SYSTEM == "Linux":
        _run("systemctl", "--user", "enable", "clock-wallpaper")
    elif SYSTEM == "Windows":
        _write_startup_vbs()


def do_disable_auto():
    if SYSTEM == "Linux":
        _run("systemctl", "--user", "disable", "clock-wallpaper")
    elif SYSTEM == "Windows":
        try:
            STARTUP_VBS.unlink()
        except OSError:
            pass


def _write_startup_vbs():
    pythonw = str(VENV_PY) if VENV_PY.exists() else "pythonw"
    STARTUP_DIR.mkdir(parents=True, exist_ok=True)
    STARTUP_VBS.write_text(
        'Dim WshShell\n'
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.Run Chr(34) & "{pythonw}" & Chr(34)'
        f' & " " & Chr(34) & "{CLOCK_PY}" & Chr(34), 0, False\n'
    )


# ── setup ─────────────────────────────────────────────────────────────────────

def do_setup(log):
    """Install deps + configure autostart. Runs in background thread."""
    py = shutil.which("python3") or shutil.which("python")
    if not py:
        raise RuntimeError("Python tidak ditemukan. Install Python terlebih dahulu.")

    if not VENV_PY.exists():
        log("Membuat virtual environment...")
        r = _run(py, "-m", "venv", str(VENV_DIR))
        if r.returncode != 0:
            raise RuntimeError(f"venv gagal:\n{r.stderr}")

    log("Menginstall Pillow (1-2 menit pertama kali)...")
    _run(str(PIP), "install", "--quiet", "--upgrade", "pip")
    r = _run(str(PIP), "install", "--quiet", "-r", str(REQ_FILE))
    if r.returncode != 0:
        raise RuntimeError(f"pip install gagal:\n{r.stderr}")

    if SYSTEM == "Linux":
        log("Membuat systemd service...")
        SERVICE_DIR.mkdir(parents=True, exist_ok=True)
        SERVICE_FILE.write_text(
            "[Unit]\n"
            "Description=Real-time Clock Wallpaper\n"
            "After=graphical-session.target\n"
            "PartOf=graphical-session.target\n\n"
            "[Service]\n"
            "Type=simple\n"
            f"ExecStart={VENV_PY} {CLOCK_PY}\n"
            "Restart=on-failure\n"
            "RestartSec=5\n\n"
            "[Install]\n"
            "WantedBy=graphical-session.target\n"
        )
        _run("systemctl", "--user", "daemon-reload")
        _run("systemctl", "--user", "enable", "clock-wallpaper")
        log("Menjalankan clock wallpaper...")
        _run("systemctl", "--user", "start", "clock-wallpaper")
        _install_desktop_shortcut()

    elif SYSTEM == "Windows":
        log("Mengaktifkan autostart saat login...")
        _write_startup_vbs()
        log("Menjalankan clock wallpaper...")
        do_start()

    log("Selesai!")


def _install_desktop_shortcut():
    """Add to application menu and Desktop (Linux)."""
    manage = str(SCRIPT_DIR / "manage.py")
    entry = (
        "[Desktop Entry]\n"
        "Name=Clock Wallpaper\n"
        "Comment=Manage the real-time clock wallpaper\n"
        f"Exec={VENV_PY} {manage}\n"
        "Terminal=false\n"
        "Type=Application\n"
        "Categories=Utility;\n"
    )
    apps = Path.home() / ".local" / "share" / "applications"
    apps.mkdir(parents=True, exist_ok=True)
    (apps / "clock-wallpaper.desktop").write_text(entry)

    desktop = Path.home() / "Desktop"
    if desktop.exists():
        sc = desktop / "Clock Wallpaper.desktop"
        sc.write_text(entry)
        sc.chmod(0o755)


# ── GUI ───────────────────────────────────────────────────────────────────────

BG     = "#1a1a2e"
CARD   = "#252545"
FG     = "#e0e0ff"
MUTED  = "#8888aa"
GREEN  = "#27ae60"
RED    = "#c0392b"
BLUE   = "#2980b9"
PURPLE = "#6c3483"
SEP    = "#2e2e5e"
W      = 340


def _mk_btn(parent, text, color, cmd, width=14):
    return tk.Button(
        parent, text=text, width=width, command=cmd,
        bg=color, fg="white", activebackground=color,
        font=("Segoe UI", 10), relief="flat", cursor="hand2",
        padx=8, pady=6, bd=0,
    )


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clock Wallpaper")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._build_ui()
        self._poll()

    # ── layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        wrap = tk.Frame(self, bg=BG, padx=20, pady=20)
        wrap.pack()

        # heading
        tk.Label(wrap, text="Clock Wallpaper", font=("Segoe UI", 15, "bold"),
                 bg=BG, fg=FG).pack()
        tk.Label(wrap, text="Real-time clock sebagai wallpaper desktop",
                 font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(pady=(2, 16))

        # status card
        card = tk.Frame(wrap, bg=CARD, padx=14, pady=12)
        card.pack(fill="x", pady=(0, 14))
        tk.Label(card, text="STATUS", font=("Segoe UI", 8, "bold"),
                 bg=CARD, fg=MUTED).pack()
        self._dot = tk.Label(card, text="●", font=("Segoe UI", 32), bg=CARD, fg=MUTED)
        self._dot.pack()
        self._lbl_status = tk.Label(card, text="Memeriksa...",
                                    font=("Segoe UI", 12, "bold"), bg=CARD, fg=MUTED)
        self._lbl_status.pack()

        # start / stop
        row1 = tk.Frame(wrap, bg=BG)
        row1.pack(fill="x", pady=(0, 12))
        self._btn_start = _mk_btn(row1, "Start", GREEN, self._on_start)
        self._btn_start.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self._btn_stop = _mk_btn(row1, "Stop", RED, self._on_stop)
        self._btn_stop.pack(side="left", expand=True, fill="x")

        tk.Frame(wrap, height=1, bg=SEP).pack(fill="x", pady=(0, 10))

        # autostart row
        row2 = tk.Frame(wrap, bg=BG)
        row2.pack(fill="x", pady=(0, 4))
        tk.Label(row2, text="Autostart:", font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(side="left")
        self._lbl_auto = tk.Label(row2, text="—", font=("Segoe UI", 10, "bold"),
                                  bg=BG, fg=MUTED)
        self._lbl_auto.pack(side="left", padx=8)
        _mk_btn(row2, "Disable", MUTED, self._on_disable_auto, width=8).pack(side="right")
        _mk_btn(row2, "Enable", BLUE, self._on_enable_auto, width=8).pack(
            side="right", padx=(0, 4))

        tk.Frame(wrap, height=1, bg=SEP).pack(fill="x", pady=10)

        # setup
        self._lbl_setup = tk.Label(wrap, text="", font=("Segoe UI", 9),
                                   bg=BG, fg=MUTED, wraplength=W - 40, justify="center")
        self._lbl_setup.pack(pady=(0, 8))
        self._btn_setup = _mk_btn(wrap, "Install / Update", PURPLE, self._on_setup, width=26)
        self._btn_setup.pack()

    # ── state refresh ─────────────────────────────────────────────────────────

    def _refresh(self):
        running  = is_running()
        autorun  = is_autostart()
        inst     = is_installed()

        color = GREEN if running else RED
        self._dot.config(fg=color)
        self._lbl_status.config(text="Berjalan" if running else "Berhenti", fg=color)

        self._btn_start.config(state="normal" if inst and not running else "disabled")
        self._btn_stop.config(state="normal" if running else "disabled")

        self._lbl_auto.config(
            text="Aktif" if autorun else "Tidak aktif",
            fg=GREEN if autorun else MUTED,
        )

        if inst:
            self._lbl_setup.config(text="Sudah terinstall. Klik untuk update dependensi.")
        else:
            self._lbl_setup.config(
                text="Belum terinstall. Klik Install untuk menyiapkan semuanya."
            )

    def _poll(self):
        self._refresh()
        self.after(3000, self._poll)

    # ── button handlers ───────────────────────────────────────────────────────

    def _on_start(self):
        do_start()
        self.after(1200, self._refresh)

    def _on_stop(self):
        do_stop()
        self.after(1200, self._refresh)

    def _on_enable_auto(self):
        do_enable_auto()
        self.after(500, self._refresh)

    def _on_disable_auto(self):
        do_disable_auto()
        self.after(500, self._refresh)

    def _on_setup(self):
        self._btn_setup.config(state="disabled", text="Menginstall...")
        self._lbl_setup.config(text="Memulai instalasi...")

        def log(msg):
            self.after(0, lambda m=msg: self._lbl_setup.config(text=m))

        def run():
            try:
                do_setup(log)
                self.after(0, self._setup_ok)
            except Exception as exc:
                self.after(0, lambda e=exc: self._setup_err(e))

        threading.Thread(target=run, daemon=True).start()

    def _setup_ok(self):
        self._btn_setup.config(state="normal", text="Install / Update")
        self._refresh()

    def _setup_err(self, exc):
        self._btn_setup.config(state="normal", text="Install / Update")
        self._lbl_setup.config(text=f"Error: {exc}")
        messagebox.showerror("Instalasi gagal", str(exc))


if __name__ == "__main__":
    App().mainloop()
