@echo off
echo Installing spotipy and fuzzywuzzy...

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)

REM Upgrade pip to the latest version
python -m pip install --upgrade pip

REM Install spotipy
pip install spotipy

REM Install fuzzywuzzy
pip install fuzzywuzzy

REM Install Dotenv
pip install python-dotenv

REM Confirm installation
echo.
echo Installation completed.
echo Spotipy, Dotenv and FuzzyWuzzy are now installed.
pause