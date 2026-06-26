# Tutra Startup Guide

This directory contains the operational scripts to run the entire Tutra platform locally with a single click.

## Prerequisites
Before running the launch script, ensure the following are installed:
1. **Docker Desktop** (Must be running)
2. **Ollama** (Must be running)
3. **Node.js** (For the frontend)
4. **Python** (For the backend)

## 1. Start Tutra
Double-click `launch.bat`.

**What it does:**
1. Verifies Docker and Ollama are active.
2. Starts PostgreSQL via `docker-compose up -d`.
3. Opens a new terminal to start the FastAPI backend (`uvicorn`).
4. Opens a new terminal to start the Next.js frontend (`npm run dev`).
5. Automatically opens `http://localhost:3000` in your default browser.

*Assumption:* It assumes `npm install` and `pip install -r requirements.txt` (or equivalent) have already been run in the respective `frontend` and `backend` directories.

## 2. Verify Health
Double-click `healthcheck.bat`.

**What it does:**
Checks the status of Docker, Ollama, PostgreSQL (Port 5432), FastAPI (Port 8000), and Next.js (Port 3000). It will output `[PASS]` or `[FAIL]` for each component.

## 3. Stop Tutra
Double-click `stop.bat`.

**What it does:**
1. Gracefully kills the terminal windows running the Frontend and Backend.
2. Runs `docker-compose down` to stop the database container.
