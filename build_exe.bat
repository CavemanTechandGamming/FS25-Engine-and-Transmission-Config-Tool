@echo off
echo Building FS25 Config Tool EXE...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

REM Build the EXE using PyInstaller
echo Running PyInstaller...
pyinstaller --onefile --windowed --name "FS25 Engine and Transmission Config Tool" --add-data "LICENSE;." --hidden-import tkinter --hidden-import tkinter.ttk --hidden-import tkinter.filedialog --hidden-import tkinter.messagebox --hidden-import tkinter.scrolledtext --hidden-import tkinter.simpledialog --hidden-import customtkinter --hidden-import json --hidden-import os --hidden-import math --hidden-import re --hidden-import threading fs25_config_tool.py

REM Check if build was successful
if exist "dist\FS25 Engine and Transmission Config Tool.exe" (
    echo.
    echo SUCCESS! EXE file created successfully.
echo Location: dist\FS25 Engine and Transmission Config Tool.exe
echo.
echo The EXE file is completely portable and can be run from any location.
echo.
echo Copy the EXE to the "FS25 Engine and Transmission Config Tool Portable Release" folder for distribution.
    echo.
    pause
) else (
    echo.
    echo ERROR: EXE file was not created successfully.
    echo Please check the error messages above.
    echo.
    pause
) 