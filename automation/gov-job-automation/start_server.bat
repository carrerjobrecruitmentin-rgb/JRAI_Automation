@echo off
title Gov-Job Automation Server (Port 8080)
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist "..\..\venv\Scripts\activate.bat" (
    call ..\..\venv\Scripts\activate.bat
) else if exist "d:\Aamir\venv\Scripts\activate.bat" (
    call d:\Aamir\venv\Scripts\activate.bat
)
python backend\run.py
pause
