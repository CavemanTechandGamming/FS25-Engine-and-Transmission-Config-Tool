@echo off
setlocal EnableExtensions EnableDelayedExpansion
REM ----------------------------------------------------------------------------
REM build_app.bat - versioned portable + installer PyInstaller builds (Windows)
REM Version comes from src\__init__.py (single source of truth).
REM
REM Outputs (example):
REM   dist\windows\1.0.0\portable\FS25ConfigTool-1.0.0.exe
REM   dist\windows\1.0.0\installer\FS25ConfigTool-1.0.0\...
REM ----------------------------------------------------------------------------

cd /d "%~dp0.."
set "PLATFORM=windows"

echo.
echo === FS25 Config Tool - PyInstaller build (Windows) ===
echo Working directory: %CD%
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Running setup_env.bat ...
    call "scripts\setup_env.bat"
    if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"

where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ERROR: pyinstaller not found in the virtual environment.
    echo Run scripts\setup_env.bat first.
    exit /b 1
)

for /f "usebackq delims=" %%V in (`python scripts\read_version.py`) do set "VERSION=%%V"
if not defined VERSION (
    echo ERROR: Could not read app version from src\__init__.py
    exit /b 1
)

set "APP_NAME=FS25ConfigTool-%VERSION%"
echo App version: %VERSION%
echo Artifact names: fs25-config-tool-%PLATFORM%-%VERSION%-portable / installer
echo.

set "COMMON_ARGS=--noconfirm --clean --windowed --name %APP_NAME% --paths=. --collect-all customtkinter"

echo [1/2] Building portable (onefile) ...
if exist "dist\%PLATFORM%\%VERSION%\portable" rmdir /s /q "dist\%PLATFORM%\%VERSION%\portable"
if exist "build\%PLATFORM%\%VERSION%\portable" rmdir /s /q "build\%PLATFORM%\%VERSION%\portable"
mkdir "dist\%PLATFORM%\%VERSION%\portable" 2>nul
mkdir "build\%PLATFORM%\%VERSION%\portable" 2>nul

python -m PyInstaller %COMMON_ARGS% ^
  --onefile ^
  --distpath "dist\%PLATFORM%\%VERSION%\portable" ^
  --workpath "build\%PLATFORM%\%VERSION%\portable" ^
  --specpath "build\%PLATFORM%\%VERSION%\portable" ^
  src\__main__.py
if errorlevel 1 (
    echo ERROR: portable build failed.
    exit /b 1
)

echo [2/2] Building installer (onedir) ...
if exist "dist\%PLATFORM%\%VERSION%\installer" rmdir /s /q "dist\%PLATFORM%\%VERSION%\installer"
if exist "build\%PLATFORM%\%VERSION%\installer" rmdir /s /q "build\%PLATFORM%\%VERSION%\installer"
mkdir "dist\%PLATFORM%\%VERSION%\installer" 2>nul
mkdir "build\%PLATFORM%\%VERSION%\installer" 2>nul

python -m PyInstaller %COMMON_ARGS% ^
  --onedir ^
  --distpath "dist\%PLATFORM%\%VERSION%\installer" ^
  --workpath "build\%PLATFORM%\%VERSION%\installer" ^
  --specpath "build\%PLATFORM%\%VERSION%\installer" ^
  src\__main__.py
if errorlevel 1 (
    echo ERROR: installer build failed.
    exit /b 1
)

echo.
echo Build complete:
echo   Portable : dist\%PLATFORM%\%VERSION%\portable\%APP_NAME%.exe
echo   Installer: dist\%PLATFORM%\%VERSION%\installer\%APP_NAME%\
echo.
exit /b 0
