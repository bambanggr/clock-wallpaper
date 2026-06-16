#!/usr/bin/env bash
# Double-click launcher untuk Clock Wallpaper Manager (Linux)
cd "$(dirname "$(readlink -f "$0")")"
if [ -f ".venv/bin/python3" ]; then
    exec .venv/bin/python3 manage.py
else
    exec python3 manage.py
fi
