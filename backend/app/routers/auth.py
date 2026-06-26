from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from app.database import get_db
from app.models import User, Organization, OrganizationUser, StudentProfile, Subscription, Plan
from app.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta, datetime
import os
import uuid

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

class GoogleLoginRequest(BaseModel):
    credential: str

@router.post("/google")
async def google_auth(request: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Verify the token
        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        if client_id:
            idinfo = id_token.verify_oauth2_token(request.credential, requests.Request(), client_id)
        else:
            # If no client ID configured for local dev, we just decode it without strict audience verification
            import jwt
            idinfo = jwt.decode(request.credential, options={"verify_signature": False})

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')

        # Check if user exists
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalars().first()

        is_new_user = False

        if not user:
            try:
                # Create new user
                is_new_user = True
                user = User(
                    google_id=google_id,
                    email=email,
                    name=name,
                    profile_picture=picture,
                    role="parent",
                    auth_provider="google"
                )
                db.add(user)
                await db.flush() # get user.id
                
                # Create Family Organization
                org = Organization(name=f"{name.split(' ')[0]}'s Family", type="family")
                db.add(org)
                await db.flush()

                # Link User to Organization
                org_user = OrganizationUser(organization_id=org.id, user_id=user.id, role="owner")
                db.add(org_user)
                
                # Create default Student Profile to satisfy relationships (will be updated in Discovery)
                student = StudentProfile(user_id=user.id)
                db.add(student)

                # Assign Free Subscription
                plan = (await db.execute(select(Plan).where(Plan.name == "Free"))).scalars().first()
                if plan:
                    db.add(Subscription(organization_id=org.id, plan_id=plan.id, status="active"))

                user.last_login = datetime.utcnow()
                await db.commit()
            except Exception as db_err:
                await db.rollback()
                raise HTTPException(status_code=500, detail="Transaction failed, rolled back.") from db_err
        else:
            # Update existing user's google info if missing
            if not user.google_id:
                user.google_id = google_id
                user.auth_provider = "google"
            if not user.profile_picture and picture:
                user.profile_picture = picture
            user.last_login = datetime.utcnow()
            await db.commit()

        # Generate JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role}, expires_delta=access_token_expires
        )

        # Get default student profile
        stmt = select(StudentProfile).where(StudentProfile.user_id == user.id)
        result = await db.execute(stmt)
        student_profile = result.scalars().first()
        student_id = str(student_profile.id) if student_profile else None

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "is_new_user": is_new_user,
            "user": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "picture": user.profile_picture,
                "role": user.role,
                "default_student_id": student_id
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Google Token: {str(e)}")
