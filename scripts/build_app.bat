@echo off
setlocal EnableExtensions EnableDelayedExpansion
REM ----------------------------------------------------------------------------
REM build_app.bat - Windows portable (onefile) + real Inno Setup installer
REM Version comes from src\__init__.py (single source of truth).
REM
REM Outputs (example):
REM   dist\windows\1.0.0\portable\FS25 Engine and Transmission Config Tool.exe
REM   dist\windows\1.0.0\installer\FS25 Engine and Transmission Config Tool-1.0.0-Setup.exe
REM ----------------------------------------------------------------------------

cd /d "%~dp0.."
set "PLATFORM=windows"
set "APP_NAME=FS25 Engine and Transmission Config Tool"

echo.
echo === %APP_NAME% - Windows build ===
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

set "PORTABLE_DIR=dist\%PLATFORM%\%VERSION%\portable"
set "INSTALLER_DIR=dist\%PLATFORM%\%VERSION%\installer"
set "PORTABLE_EXE=%PORTABLE_DIR%\%APP_NAME%.exe"
set "SETUP_NAME=%APP_NAME%-%VERSION%-Setup"

echo App version: %VERSION%
echo.

echo [1/2] Building portable (onefile) ...
if exist "%PORTABLE_DIR%" rmdir /s /q "%PORTABLE_DIR%"
if exist "build\%PLATFORM%\%VERSION%\portable" rmdir /s /q "build\%PLATFORM%\%VERSION%\portable"
mkdir "%PORTABLE_DIR%" 2>nul
mkdir "build\%PLATFORM%\%VERSION%\portable" 2>nul

python -m PyInstaller --noconfirm --clean --windowed --onefile ^
  --name "%APP_NAME%" --paths=. --collect-all customtkinter ^
  --distpath "%PORTABLE_DIR%" ^
  --workpath "build\%PLATFORM%\%VERSION%\portable" ^
  --specpath "build\%PLATFORM%\%VERSION%\portable" ^
  src\__main__.py
if errorlevel 1 (
    echo ERROR: portable build failed.
    exit /b 1
)
if not exist "%PORTABLE_EXE%" (
    echo ERROR: Expected portable exe not found: %PORTABLE_EXE%
    exit /b 1
)

echo [2/2] Building Windows installer (Inno Setup) ...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC (
    where iscc >nul 2>&1
    if not errorlevel 1 for /f "delims=" %%I in ('where iscc') do (
        if not defined ISCC set "ISCC=%%I"
    )
)

if not defined ISCC (
    echo ERROR: Inno Setup 6 ISCC.exe not found.
    echo Install from https://jrsoftware.org/isinfo.php or: choco install innosetup -y
    exit /b 1
)
echo Using ISCC: %ISCC%

if exist "%INSTALLER_DIR%" rmdir /s /q "%INSTALLER_DIR%"
mkdir "%INSTALLER_DIR%" 2>nul

for %%I in ("%PORTABLE_EXE%") do set "SOURCE_EXE=%%~fI"
for %%I in ("%INSTALLER_DIR%") do set "OUT_DIR=%%~fI"

"%ISCC%" ^
  "/DMyAppVersion=%VERSION%" ^
  "/DSourceExe=%SOURCE_EXE%" ^
  "/DOutputDir=%OUT_DIR%" ^
  "/DOutputBaseFilename=%SETUP_NAME%" ^
  "packaging\windows\setup.iss"
if errorlevel 1 (
    echo ERROR: Inno Setup compile failed.
    exit /b 1
)

if not exist "%INSTALLER_DIR%\%SETUP_NAME%.exe" (
    echo ERROR: Expected setup exe not found: %INSTALLER_DIR%\%SETUP_NAME%.exe
    exit /b 1
)

echo.
echo Build complete:
echo   Portable : %PORTABLE_EXE%
echo   Installer: %INSTALLER_DIR%\%SETUP_NAME%.exe
echo.
exit /b 0
