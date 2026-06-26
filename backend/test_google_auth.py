import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, get_db
from app.models import Base, User, Organization, Subscription
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json
import jwt

# Mock google auth
from unittest.mock import patch

client = TestClient(app)

async def test_flow():
    # 1. Clear db for clean test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # ensure free plan
    from app.models import Plan
    async with AsyncSession(engine) as db:
        db.add(Plan(name="Free", monthly_price=0.0, yearly_price=0.0))
        await db.commit()

    print("\n--- SIMULATING GOOGLE LOGIN REQUEST ---")
    mock_idinfo = {
        "iss": "https://accounts.google.com",
        "sub": "1234567890abcdef",
        "email": "testparent@gmail.com",
        "name": "Test Parent",
        "picture": "https://lh3.googleusercontent.com/a/mockpicture"
    }
    
    with patch("app.routers.auth.id_token.verify_oauth2_token", return_value=mock_idinfo):
        response = client.post("/api/v1/auth/google", json={"credential": "mock_google_id_token_from_frontend"})
        
    print("\n--- RESPONSE JSON (/api/v1/auth/google) ---")
    print(json.dumps(response.json(), indent=2))
    
    access_token = response.json()["access_token"]
    
    print("\n--- JWT PAYLOAD ---")
    decoded = jwt.decode(access_token, options={"verify_signature": False})
    print(json.dumps(decoded, indent=2))
    
    print("\n--- DATABASE: USERS TABLE ---")
    async with AsyncSession(engine) as db:
        users = (await db.execute(select(User))).scalars().all()
        for u in users:
            print(f"ID: {u.id} | Email: {u.email} | Google ID: {u.google_id} | Role: {u.role} | Last Login: {u.last_login}")

    print("\n--- DATABASE: ORGANIZATIONS TABLE ---")
    async with AsyncSession(engine) as db:
        orgs = (await db.execute(select(Organization))).scalars().all()
        for o in orgs:
            print(f"ID: {o.id} | Name: {o.name} | Type: {o.type}")

    print("\n--- DATABASE: SUBSCRIPTIONS TABLE ---")
    async with AsyncSession(engine) as db:
        subs = (await db.execute(select(Subscription))).scalars().all()
        for s in subs:
            print(f"ID: {s.id} | Org ID: {s.organization_id} | Plan ID: {s.plan_id} | Status: {s.status}")

if __name__ == "__main__":
    asyncio.run(test_flow())
