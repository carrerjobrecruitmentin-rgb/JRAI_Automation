@echo off
title Gov-Job Smart Automation Crawler
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist "..\..\venv\Scripts\activate.bat" (
    call ..\..\venv\Scripts\activate.bat
) else if exist "d:\Aamir\venv\Scripts\activate.bat" (
    call d:\Aamir\venv\Scripts\activate.bat
)
python automation\engine\orchestrator.py
pause
