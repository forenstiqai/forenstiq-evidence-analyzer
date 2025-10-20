@echo off
REM Build script for Windows executable

echo ==========================================
echo Forenstiq Evidence Analyzer - Windows Build
echo ==========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Clean previous builds
echo Cleaning previous builds...
rmdir /s /q build dist 2>nul

REM Build the executable
echo.
echo Building Windows application...
pyinstaller --clean --noconfirm forenstiq.spec

REM Check if build was successful
if exist "dist\Forenstiq\Forenstiq.exe" (
    echo.
    echo ==========================================
    echo Build successful!
    echo ==========================================
    echo.
    echo Application location:
    echo   dist\Forenstiq\
    echo.
    echo To distribute:
    echo   1. Copy the entire 'dist\Forenstiq' folder to any Windows PC
    echo   2. Run Forenstiq.exe
    echo.
    echo To create an installer, use tools like:
    echo   - Inno Setup
    echo   - NSIS
    echo   - WiX Toolset
    echo.
) else (
    echo.
    echo ==========================================
    echo Build failed!
    echo ==========================================
    echo Check the output above for errors.
    exit /b 1
)
