@echo off
setlocal

echo =======================================
echo        TUTRA HEALTH CHECK
echo =======================================
echo.

echo Checking Docker...
docker info >nul 2>&1
if %errorlevel% equ 0 (echo [PASS] Docker is running.) else (echo [FAIL] Docker is not running.)

echo.
echo Checking Ollama...
ollama list >nul 2>&1
if %errorlevel% equ 0 (echo [PASS] Ollama is running.) else (echo [FAIL] Ollama is not running.)

echo.
echo Checking PostgreSQL (Port 5432)...
netstat -ano | find "LISTENING" | find ":5432" >nul 2>&1
if %errorlevel% equ 0 (echo [PASS] Database is listening.) else (echo [FAIL] Database is not running.)

echo.
echo Checking Backend (Port 8000)...
netstat -ano | find "LISTENING" | find ":8000" >nul 2>&1
if %errorlevel% equ 0 (echo [PASS] Backend is listening.) else (echo [FAIL] Backend is not running.)

echo.
echo Checking Frontend (Port 3000)...
netstat -ano | find "LISTENING" | find ":3000" >nul 2>&1
if %errorlevel% equ 0 (echo [PASS] Frontend is listening.) else (echo [FAIL] Frontend is not running.)

echo.
echo =======================================
echo        HEALTH CHECK COMPLETE
echo =======================================
pause
