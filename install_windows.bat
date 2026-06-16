@echo off
setlocal

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%.venv
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

:: Create virtual environment if missing
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ERROR: Failed to create venv. Make sure Python has venv support.
        pause
        exit /b 1
    )
)

:: Install dependencies
echo Installing dependencies...
"%VENV_DIR%\Scripts\pip.exe" install --quiet --upgrade pip
"%VENV_DIR%\Scripts\pip.exe" install --quiet -r "%SCRIPT_DIR%requirements.txt"

:: Copy VBS launcher to startup folder
copy /Y "%VBS_RUNNER%" "%STARTUP%\clock_wallpaper.vbs" >nul

echo.
echo Done! Clock wallpaper will start automatically on next login.
echo.
echo To start now, run: wscript "%VBS_RUNNER%"
echo To stop: kill pythonw.exe in Task Manager
echo.
pause
