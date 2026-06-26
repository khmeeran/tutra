@echo off
setlocal

echo =======================================
echo        LAUNCHING TUTRA PLATFORM
echo =======================================
echo.

:: 1. Verify Docker is running
echo [1/5] Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b
)

:: 6. Verify Ollama is running
echo [2/5] Checking Ollama status...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Ollama is not running. Please start Ollama to enable AI features.
    pause
    exit /b
)

:: 2. Start PostgreSQL via docker-compose
echo [3/5] Starting Database...
docker-compose up -d

:: 3. Wait for DB
echo Waiting 5 seconds for Database to initialize...
timeout /t 5 /nobreak >nul

:: 4. Start Backend in new window
echo [4/5] Starting Backend (FastAPI)...
start "Tutra Backend" cmd /c "cd backend && call venv\Scripts\activate && echo Starting Uvicorn... && uvicorn app.main:app --reload"

:: 5. Start Frontend in new window
echo [5/5] Starting Frontend (Next.js)...
start "Tutra Frontend" cmd /c "cd frontend && echo Starting Next.js... && npm run dev"

echo Waiting 8 seconds for services to boot...
timeout /t 8 /nobreak >nul

:: 7. Open Browser
echo Opening Browser...
start http://localhost:3000

echo.
echo =======================================
echo        TUTRA IS NOW RUNNING!
echo =======================================
echo To stop all services, run stop.bat
echo.
pause
