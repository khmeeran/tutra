@echo off
setlocal

echo =======================================
echo        STOPPING TUTRA PLATFORM
echo =======================================
echo.

echo [1/3] Stopping Frontend...
taskkill /fi "WINDOWTITLE eq Tutra Frontend*" /t /f >nul 2>&1
if %errorlevel% equ 0 (echo   Frontend stopped.) else (echo   Frontend was not running.)

echo [2/3] Stopping Backend...
taskkill /fi "WINDOWTITLE eq Tutra Backend*" /t /f >nul 2>&1
if %errorlevel% equ 0 (echo   Backend stopped.) else (echo   Backend was not running.)

echo [3/3] Stopping Database (Docker)...
docker-compose down

echo.
echo =======================================
echo        TUTRA SHUTDOWN COMPLETE
echo =======================================
pause
