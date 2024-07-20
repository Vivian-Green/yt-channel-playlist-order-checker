@echo off

REM Check if Python 3 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 is required but not found on your system.
    echo Please install Python 3 from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install pytube using pip
pip install pytube3

REM Install yt-dlp using pip
pip install yt-dlp

REM Verify installations
pip show pytube3
pip show yt-dlp

REM Prompt user to run main.py
set /p run_main=Do you want to run main.py now? (y/n): 
if /i "%run_main%"=="y" (
    python main.py
) else (
    echo Exiting script.
)

REM Pause at the end to keep the window open
pause
