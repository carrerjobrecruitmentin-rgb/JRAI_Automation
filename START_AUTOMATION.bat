@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
TITLE JobRecruitmentAI - Automation Engine
COLOR 0B

echo.
echo ================================================================
echo   JOBRECRUITMENTAI - MASTER AUTOMATION LAUNCHER
echo   E:\ Drive Worker Engine  ^|  jobrecruitment.ai
echo ================================================================
echo.

:: ================================================================
:: STEP 1: Resolve Python Executable
:: ================================================================
set PYTHON_EXE=
set UVICORN_EXE=

if exist "E:\automation\gov-job-automation\venv\Scripts\python.exe" (
    set PYTHON_EXE=E:\automation\gov-job-automation\venv\Scripts\python.exe
    set UVICORN_EXE=E:\automation\gov-job-automation\venv\Scripts\uvicorn.exe
    echo [ENV] Using venv: E:\automation\gov-job-automation\venv
    goto :python_found
)

where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_EXE=python
    set UVICORN_EXE=uvicorn
    echo [ENV] Using system Python
    goto :python_found
)

echo [ERROR] Python not found! Install Python or check venv path.
pause
exit /b 1

:python_found
echo [ENV] Python: %PYTHON_EXE%
echo.

:: ================================================================
:: STEP 2: Set Default Ports (read from E:\.env if keys exist)
:: ================================================================
set CV_PORT=8000
set AI_PORT=8005

if exist "E:\.env" (
    for /f "usebackq eol=# tokens=1,* delims==" %%A in ("E:\.env") do (
        set _KEY=%%A
        set _VAL=%%B
        set _KEY=!_KEY: =!
        if "!_KEY!"=="CV_PARSER_PORT"   set CV_PORT=!_VAL!
        if "!_KEY!"=="GOV_JOB_API_PORT" set AI_PORT=!_VAL!
    )
)
set CV_PORT=%CV_PORT:"=%
set AI_PORT=%AI_PORT:"=%
set CV_PORT=%CV_PORT: =%
set AI_PORT=%AI_PORT: =%

echo [CFG] CV Parser Port  : %CV_PORT%
echo [CFG] AI Matcher Port : %AI_PORT%
echo.

:: ================================================================
:: STEP 3: Check if workers already running — ask user
:: ================================================================
set ALREADY_RUNNING=0

netstat -ano 2>nul | findstr ":%CV_PORT% " | findstr "LISTENING" >nul
if %errorlevel% equ 0 set ALREADY_RUNNING=1

netstat -ano 2>nul | findstr ":%AI_PORT% " | findstr "LISTENING" >nul
if %errorlevel% equ 0 set ALREADY_RUNNING=1

if %ALREADY_RUNNING%==1 (
    echo ================================================================
    echo   [!] WORKERS ALREADY RUNNING DETECTED
    echo.
    echo   Port %CV_PORT% ^(CV Parser^)   - ACTIVE
    echo   Port %AI_PORT% ^(AI Matcher^)  - ACTIVE
    echo.
    echo   What do you want to do?
    echo   [R] Restart  - Stop old workers and start fresh
    echo   [K] Keep     - Keep existing workers running ^(exit^)
    echo ================================================================
    echo.
    set /p USER_CHOICE="Enter R to Restart or K to Keep [R/K]: "
    echo.

    if /i "!USER_CHOICE!"=="K" (
        echo [OK] Keeping existing workers. Automation is already active.
        echo.
        timeout /t 3 /nobreak >nul
        exit /b 0
    )

    :: User chose R — Kill existing workers first
    echo [RESTART] Stopping existing workers before restart...
    echo.

    for /f "tokens=5" %%P in ('netstat -ano 2^>nul ^| findstr ":%CV_PORT% " ^| findstr "LISTENING"') do (
        echo   [KILL] Stopping CV Parser PID %%P
        taskkill /PID %%P /F >nul 2>nul
    )
    for /f "tokens=5" %%P in ('netstat -ano 2^>nul ^| findstr ":%AI_PORT% " ^| findstr "LISTENING"') do (
        echo   [KILL] Stopping AI Matcher PID %%P
        taskkill /PID %%P /F >nul 2>nul
    )
    taskkill /IM cloudflared.exe /F >nul 2>nul
    echo   [OK] Old workers stopped. Starting fresh...
    echo.
    timeout /t 2 /nobreak >nul
)

:: ================================================================
:: STEP 4: Start CV Parser (FastAPI + uvicorn)
:: ================================================================
echo [1/3] CV Parser and OCR Server (Port %CV_PORT%)...

if exist "E:\automation\cv_parser_server.py" (
    if exist "%UVICORN_EXE%" (
        start "CV Parser [Port %CV_PORT%]" cmd /k "cd /d E:\automation && "%UVICORN_EXE%" cv_parser_server:app --host 0.0.0.0 --port %CV_PORT%"
    ) else (
        start "CV Parser [Port %CV_PORT%]" cmd /k "cd /d E:\automation && "%PYTHON_EXE%" -m uvicorn cv_parser_server:app --host 0.0.0.0 --port %CV_PORT%"
    )
    echo   [STARTED] CV Parser  -  http://127.0.0.1:%CV_PORT%
) else (
    echo   [WARNING] cv_parser_server.py not found at E:\automation\
)
timeout /t 2 /nobreak >nul
echo.

:: ================================================================
:: STEP 5: Start AI Matching Webhook
:: ================================================================
echo [2/3] AI Candidate-Job Matching Webhook (Port %AI_PORT%)...

if exist "E:\automation\ai_match_webhook.py" (
    start "AI Matcher [Port %AI_PORT%]" cmd /k "cd /d E:\automation && "%PYTHON_EXE%" ai_match_webhook.py"
    echo   [STARTED] AI Matcher  -  http://127.0.0.1:%AI_PORT%
) else (
    echo   [WARNING] ai_match_webhook.py not found at E:\automation\
)
timeout /t 2 /nobreak >nul
echo.

:: ================================================================
:: STEP 6: Start Cloudflare Ingress Tunnel
:: ================================================================
echo [3/3] Cloudflare Ingress Tunnel...

set CF_BIN=cloudflared
if exist "C:\cloudflared\cloudflared.exe"                          set CF_BIN=C:\cloudflared\cloudflared.exe
if exist "C:\Program Files\cloudflared\cloudflared.exe"            set CF_BIN=C:\Program Files\cloudflared\cloudflared.exe
if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe"      set CF_BIN=C:\Program Files (x86)\cloudflared\cloudflared.exe

tasklist /FI "IMAGENAME eq cloudflared.exe" 2>nul | findstr /I "cloudflared" >nul
if %errorlevel% equ 0 (
    echo   [OK] Cloudflare tunnel already running - skipping.
) else (
    if exist "E:\automation\cloudflare\config.yml" (
        start "Cloudflare Tunnel [jobrecruitment.ai]" cmd /k ""!CF_BIN!" tunnel --config E:\automation\cloudflare\config.yml run 5a170a20-224b-4542-886c-87733cf0d822"
        echo   [STARTED] Cloudflare Tunnel active for jobrecruitment.ai
    ) else (
        echo   [INFO] cloudflare\config.yml not found - workers on localhost only.
    )
)
echo.
timeout /t 3 /nobreak >nul

:: ================================================================
:: Done — show how to stop
:: ================================================================
echo ================================================================
echo   [SUCCESS] ALL AUTOMATION WORKERS INITIALIZED!
echo.
echo   Service         URL
echo   -------         ---
echo   CV Parser       http://127.0.0.1:%CV_PORT%/health
echo   AI Matcher      http://127.0.0.1:%AI_PORT%/health
echo   Cloudflare CV   https://cv-parser.jobrecruitment.ai/health
echo   Admin Center    https://jobrecruitment.ai/admin-automation-workers
echo.
echo   To STOP all workers: Run STOP_AUTOMATION.bat
echo ================================================================
echo.
echo  Workers run in background windows. This launcher can be closed.
echo  Press any key to close this launcher.
pause
