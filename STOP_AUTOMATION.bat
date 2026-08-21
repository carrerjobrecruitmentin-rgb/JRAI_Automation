@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
TITLE JobRecruitmentAI - Stop All Workers
COLOR 0C

echo.
echo ================================================================
echo   JOBRECRUITMENTAI - STOP ALL AUTOMATION WORKERS
echo ================================================================
echo.

:: Load ports from .env (same logic as START_AUTOMATION.bat)
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

echo [1/3] Stopping CV Parser on Port %CV_PORT%...
for /f "tokens=5" %%P in ('netstat -ano 2^>nul ^| findstr ":%CV_PORT% " ^| findstr "LISTENING"') do (
    echo   [KILL] PID %%P
    taskkill /PID %%P /F >nul 2>nul
)
echo   [OK] CV Parser stopped.

echo.
echo [2/3] Stopping AI Matching Webhook on Port %AI_PORT%...
for /f "tokens=5" %%P in ('netstat -ano 2^>nul ^| findstr ":%AI_PORT% " ^| findstr "LISTENING"') do (
    echo   [KILL] PID %%P
    taskkill /PID %%P /F >nul 2>nul
)
echo   [OK] AI Matcher stopped.

echo.
echo [3/3] Stopping Cloudflare Tunnel...
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>nul | findstr /I "cloudflared" >nul
if %errorlevel% equ 0 (
    taskkill /IM cloudflared.exe /F >nul 2>nul
    echo   [OK] Cloudflare tunnel stopped.
) else (
    echo   [INFO] Cloudflare tunnel was not running.
)

echo.
echo ================================================================
echo   [DONE] All automation workers have been stopped.
echo   Run START_AUTOMATION.bat to restart them.
echo ================================================================
echo.
pause
