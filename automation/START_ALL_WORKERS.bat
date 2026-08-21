@echo off
TITLE JobRecruitmentAI - Master Automation Launcher (E:\ & D:\)
COLOR 0A

echo ===============================================================================
echo        JOBRECRUITMENTAI - ONE-CLICK MASTER WORKER LAUNCHER
echo ===============================================================================
echo.

:: 1. Start CV Parser FastAPI Server (Port 8000)
echo [1/3] Starting FastAPI CV Parser Server on Port 8000...
if exist "E:\automation\cv_parser_server.py" (
    start "CV Parser Server (Port 8000)" cmd /k "cd /d E:\automation && uvicorn cv_parser_server:app --host 0.0.0.0 --port 8000"
    echo [OK] CV Parser launched on http://127.0.0.1:8000
) else (
    echo [WARNING] E:\automation\cv_parser_server.py not found.
)
timeout /t 2 /nobreak >nul
echo.

:: 2. Start AI Matching Webhook Engine (Port 8005)
echo [2/3] Starting AI Candidate-Job Matching Webhook on Port 8005...
if exist "E:\automation\ai_match_webhook.py" (
    start "AI Matching Webhook (Port 8005)" cmd /k "cd /d E:\automation && python ai_match_webhook.py"
    echo [OK] AI Matching Webhook launched on http://127.0.0.1:8005
) else (
    echo [WARNING] E:\automation\ai_match_webhook.py not found.
)
timeout /t 2 /nobreak >nul
echo.

:: 3. Check Cloudflare Tunnel CLI
echo [3/3] Checking Cloudflare Tunnel (cloudflared)...
set CLOUDFLARED_BIN=cloudflared
if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" set CLOUDFLARED_BIN="C:\Program Files (x86)\cloudflared\cloudflared.exe"
if exist "C:\Program Files\cloudflared\cloudflared.exe" set CLOUDFLARED_BIN="C:\Program Files\cloudflared\cloudflared.exe"

if exist "E:\automation\cloudflare\config.yml" (
    echo [OK] Starting Cloudflare tunnel with config E:\automation\cloudflare\config.yml...
    start "Cloudflare Tunnel (E:)" cmd /k "%CLOUDFLARED_BIN% tunnel --config E:\automation\cloudflare\config.yml run 5a170a20-224b-4542-886c-87733cf0d822"
) else (
    echo [INFO] Local workers will run directly on 127.0.0.1.
)

echo.
echo ===============================================================================
echo   [SUCCESS] ALL BACKGROUND AUTOMATION WORKERS INITIALIZED!
echo   - CV Parser: http://127.0.0.1:8000
echo   - AI Matcher: http://127.0.0.1:8005
echo   - Admin Health: http://127.0.0.1:8080/public_html/admin-automation-workers.html
echo ===============================================================================
echo.
echo Press any key to close this launcher window (Workers remain active in background).
pause >nul
