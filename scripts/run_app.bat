@echo off
REM ----------------------------------------------------------------------------
REM run_app.bat - launch FS25 Config Tool for a quick smoke test (no build)
REM ----------------------------------------------------------------------------

cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Running setup_env.bat ...
    call "scripts\setup_env.bat"
    if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"
echo Starting FS25 Engine and Transmission Config Tool ...
python -m src
exit /b %ERRORLEVEL%
