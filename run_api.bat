@echo off
echo ========================================
echo Starting Solar Radiation Prediction API
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found!
    echo Please create it first with: python -m venv .venv
    pause
    exit /b 1
)

echo Using virtual environment...
echo.

REM Install dependencies using venv's pip
echo Installing required packages...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Warning: Some packages may not have been installed!
    echo This might be due to missing build tools.
    echo.
    echo Trying to install pre-built wheels...
    REM Try installing with pre-built wheels only
    .venv\Scripts\python.exe -m pip install --only-binary :all: -r requirements.txt
    echo.
)

REM Change to app directory and run the API
echo.
echo Starting API server...
cd app
..\\.venv\Scripts\python.exe app.py

REM If the python script exits, pause to see any error messages
if errorlevel 1 (
    echo.
    echo ========================================
    echo API stopped with an error!
    echo ========================================
    pause
) else (
    echo.
    echo ========================================
    echo API stopped successfully!
    echo ========================================
    pause
)
