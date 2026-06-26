import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import engine, get_db
from app.models import Base, User, Organization, Subscription, Plan
from app.routers.auth import google_auth, GoogleLoginRequest
from unittest.mock import patch
import json
from jose import jwt
from fastapi import Depends

async def run_test():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSession(engine) as db:
        db.add(Plan(name="Free", monthly_price=0.0, yearly_price=0.0))
        await db.commit()

    mock_idinfo = {
        "iss": "https://accounts.google.com",
        "sub": "100200300400500",
        "email": "sarah.parent@gmail.com",
        "name": "Sarah Connor",
        "picture": "https://lh3.googleusercontent.com/a/mockpicture"
    }

    async with AsyncSession(engine) as db:
        with patch("app.routers.auth.id_token.verify_oauth2_token", return_value=mock_idinfo):
            req = GoogleLoginRequest(credential="fake_google_token")
            res = await google_auth(req, db)
            
            print("\n" + "="*50)
            print(" NETWORK TAB: /api/v1/auth/google RESPONSE JSON")
            print("="*50)
            print(json.dumps(res, indent=2))
            
            print("\n" + "="*50)
            print(" JWT PAYLOAD (Decoded)")
            print("="*50)
            decoded = jwt.decode(res["access_token"], options={"verify_signature": False})
            print(json.dumps(decoded, indent=2))

            print("\n" + "="*50)
            print(" DATABASE: USERS TABLE")
            print("="*50)
            users = (await db.execute(select(User))).scalars().all()
            for u in users:
                print(f"ID: {u.id} | Email: {u.email} | Google ID: {u.google_id} | Role: {u.role} | Last Login: {u.last_login}")

            print("\n" + "="*50)
            print(" DATABASE: ORGANIZATIONS TABLE")
            print("="*50)
            orgs = (await db.execute(select(Organization))).scalars().all()
            for o in orgs:
                print(f"ID: {o.id} | Name: {o.name} | Type: {o.type}")

            print("\n" + "="*50)
            print(" DATABASE: SUBSCRIPTIONS TABLE")
            print("="*50)
            subs = (await db.execute(select(Subscription))).scalars().all()
            for s in subs:
                print(f"ID: {s.id} | Org ID: {s.organization_id} | Plan ID: {s.plan_id} | Status: {s.status}")

if __name__ == "__main__":
    asyncio.run(run_test())
