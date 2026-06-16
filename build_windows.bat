@echo off
setlocal

set SCRIPT_DIR=%~dp0

echo === Building ClockWallpaper.exe ===

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

echo Installing build dependencies...
python -m pip install --quiet --upgrade pip pyinstaller
python -m pip install --quiet -r "%SCRIPT_DIR%requirements.txt"

echo Building single-file executable...
python -m PyInstaller --onefile --windowed --name ClockWallpaper ^
    --distpath "%SCRIPT_DIR%dist" ^
    --workpath "%SCRIPT_DIR%build" ^
    --specpath "%SCRIPT_DIR%build" ^
    "%SCRIPT_DIR%manage.py"

if errorlevel 1 (
    echo ERROR: build failed.
    pause
    exit /b 1
)

echo.
echo Done! Executable: %SCRIPT_DIR%dist\ClockWallpaper.exe
echo Copy that single file anywhere and double-click it to run.
echo.
pause
