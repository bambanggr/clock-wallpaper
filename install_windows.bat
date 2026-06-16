@echo off
setlocal

set SCRIPT_DIR=%~dp0
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set VBS_RUNNER=%SCRIPT_DIR%start_wallpaper.vbs

echo === Clock Wallpaper Installer (Windows) ===

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

:: Install Pillow
echo Installing dependencies...
pip install -r "%SCRIPT_DIR%requirements.txt"

:: Copy VBS launcher to startup folder
copy /Y "%VBS_RUNNER%" "%STARTUP%\clock_wallpaper.vbs" >nul

echo.
echo Done! Clock wallpaper will start automatically on next login.
echo.
echo To start now, run: wscript "%VBS_RUNNER%"
echo To stop: kill python.exe in Task Manager
echo.
pause
