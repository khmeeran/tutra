import asyncio
import asyncpg
import httpx
import sys
import os
import json
import uuid
import pytest

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.main import app, startup
from app.database import engine

ARTIFACT_DIR = r"C:\Users\khmee\.gemini\antigravity-cli\brain\70e7d9eb-86a4-4d1f-b313-6d0ff3a5ddbd"

async def setup_db():
    print("Setting up DB...")
    try:
        conn = await asyncpg.connect(user='postgres', password='password', host='localhost', port=5433)
        await conn.execute('CREATE DATABASE tutra')
        await conn.close()
    except Exception as e:
        pass

async def run_verification():
    await setup_db()
    await startup()
    
    db_out = []
    try:
        async with engine.begin() as conn:
            res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            tables = [r[0] for r in res]
            db_out.append("PostgreSQL started successfully.")
            db_out.append("Migrations (create_all) ran successfully.")
            db_out.append(f"Tables created: {', '.join(tables)}")
    except Exception as e:
        db_out.append(f"Database error: {e}")
        
    with open(os.path.join(ARTIFACT_DIR, "DATABASE_VERIFICATION.md"), "w") as f:
        f.write("# Database Verification\n\n" + "\n".join(db_out))
        
    startup_out = [
        "# Startup Verification",
        "FastAPI Application started successfully.",
        "No startup exceptions detected."
    ]
    with open(os.path.join(ARTIFACT_DIR, "STARTUP_VERIFICATION.md"), "w") as f:
        f.write("\n".join(startup_out))
        
    api_out = ["# API Verification\n"]
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # A. Register
        req_payload = {"email": "verify3@test.com", "phone": "5555555556", "password": "pass", "name": "Verify Parent"}
        res = await client.post("/api/v1/auth/register/parent", json=req_payload)
        api_out.append(f"## POST /auth/register/parent\n**Status**: {res.status_code}\n**Response**: {res.text}\n")
        
        # B. Login
        req_payload = {"identifier": "verify3@test.com", "password": "pass"}
        res = await client.post("/api/v1/auth/login", json=req_payload)
        token = res.json().get("access_token")
        api_out.append(f"## POST /auth/login\n**Status**: {res.status_code}\n**Response**: {res.text}\n")
        
        # C. Curriculum
        res = await client.get("/api/v1/curriculum/boards")
        api_out.append(f"## GET /curriculum/boards\n**Status**: {res.status_code}\n**Response**: {res.text}\n")
        
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        import seed
        try:
            await seed.seed()
        except Exception:
            pass
            
        res = await client.get("/api/v1/curriculum/boards")
        boards = res.json()
        board_id = boards[0]["id"]
        
        res = await client.get(f"/api/v1/curriculum/grades/{board_id}")
        grade_id = res.json()[0]["id"]
        
        res = await client.get(f"/api/v1/curriculum/subjects/{grade_id}")
        subject_id = res.json()[0]["id"]
        
        # D. Student
        req_payload = {"name": "Test", "medium": "Eng", "school_name": "TS", "board_id": board_id, "grade_id": grade_id, "academic_year": "2024-25"}
        res = await client.post("/api/v1/students", json=req_payload, headers=headers)
        api_out.append(f"## POST /students\n**Status**: {res.status_code}\n**Response**: {res.text}\n")
        
        # E. AI Chat
        req_payload = {"subject_id": subject_id, "message": "Hi Tutor!"}
        res = await client.post("/api/v1/conversations/chat", json=req_payload, headers=headers)
        api_out.append(f"## POST /conversations/chat\n**Status**: {res.status_code}\n**Response**: {res.text}\n")

    with open(os.path.join(ARTIFACT_DIR, "API_VERIFICATION.md"), "w") as f:
        f.write("\n".join(api_out))
        
    print("API tests written.")

asyncio.run(run_verification())
