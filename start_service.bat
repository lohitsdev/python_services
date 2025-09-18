@echo off
echo 🐍 Starting PDF Extractor Service...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Start the service
echo 🚀 Starting PDF Extractor Service on port 5001...
echo.
echo Service will be available at: http://localhost:5001
echo Press Ctrl+C to stop the service
echo.

python pdf_extractor.py
