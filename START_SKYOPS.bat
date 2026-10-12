@echo off
title SkyOps Copilot - Airline Operations Platform
cd /d "%~dp0"

echo ======================================================================
echo    DANG KHOI DONG SKYOPS COPILOT PLATFORM...
echo ======================================================================
echo.
echo  [1/2] Dang mo trinh duyet tu dong...
start "" http://skyops.local:8000

echo  [2/2] Dang chay may chu SkyOps Copilot...
echo.
echo ======================================================================
echo  Web dang chay tai: http://skyops.local:8000
echo  (Vui long giu cua so nay mo trong luc su dung web)
echo ======================================================================
echo.

.venv\Scripts\uvicorn ml.api:app --host 0.0.0.0 --port 8000
pause
