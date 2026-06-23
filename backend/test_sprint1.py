import pytest
import httpx
import uuid
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_sprint1_journey():
    async with AsyncClient(base_url=BASE_URL) as client:
        # 1. Register Parent
        reg_res = await client.post("/api/v1/auth/register/parent", json={
            "email": "testparent@example.com",
            "phone": "9998887776",
            "password": "password123",
            "name": "Test Parent"
        })
        assert reg_res.status_code in (200, 201)
        token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Login
        login_res = await client.post("/api/v1/auth/login", json={
            "identifier": "testparent@example.com",
            "password": "password123"
        })
        assert login_res.status_code == 200
        
        # 3. Create Student (Assumes seed data exists, we pass fake UUIDs to see if it accepts the payload)
        # In a real test, you'd fetch the seeded Board/Grade. Using random for schema validation here.
        student_res = await client.post("/api/v1/students", json={
            "name": "Test Student",
            "medium": "English",
            "school_name": "Test School",
            "board_id": str(uuid.uuid4()),
            "grade_id": str(uuid.uuid4()),
            "academic_year": "2024-25"
        }, headers=headers)
        assert student_res.status_code == 200
        
        # Note: Testing Ollama local integration might timeout or fail if Ollama isn't running
        print("Journey tested successfully. To test chat, use manual curl or UI.")
