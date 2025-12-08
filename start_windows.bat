@echo off
echo ==========================================
echo   AI Prompt Generator Platform
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Please install Python 3.12 or higher
    pause
    exit /b 1
)

echo [OK] Python installed

REM Check virtual environment
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check dependencies
if not exist "venv\Lib\site-packages\flask" (
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    echo [OK] Dependencies installed
)

REM Check .env file
if not exist ".env" (
    echo.
    echo [WARNING] .env file not found
    echo Copying .env.example...
    copy .env.example .env
    echo [OK] Please edit .env and add your API Key
    echo.
    pause
)

REM Start application
echo.
echo ==========================================
echo Starting AI Prompt Generator Platform...
echo ==========================================
echo.

python app.py

pause
