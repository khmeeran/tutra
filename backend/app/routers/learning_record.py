from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models import StudentActivityLog, ConceptMastery, StudentProfile, User
from pydantic import BaseModel
import uuid
from typing import Dict, Any, List
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/slr", tags=["Student Learning Record"])

class ActivityLogCreate(BaseModel):
    student_profile_id: uuid.UUID
    activity_type: str
    subject: str = None
    concept: str = None
    metadata_json: Dict[str, Any] = {}

@router.post("/log")
async def log_activity(data: ActivityLogCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Logs an activity into the Student Learning Record (SLR)"""
    # Ownership Check
    stmt = select(StudentProfile).where(StudentProfile.id == data.student_profile_id)
    profile = (await db.execute(stmt)).scalars().first()
    if not profile or profile.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this student profile")
    log = StudentActivityLog(
        student_profile_id=data.student_profile_id,
        activity_type=data.activity_type,
        subject=data.subject,
        concept=data.concept,
        metadata_json=data.metadata_json
    )
    db.add(log)
    await db.commit()
    return {"status": "logged", "id": str(log.id)}

@router.get("/insights/{student_profile_id}")
async def get_insights(student_profile_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Generates the actual dashboard insights from the SLR source of truth"""
    # Ownership Check
    stmt = select(StudentProfile).where(StudentProfile.id == student_profile_id)
    profile = (await db.execute(stmt)).scalars().first()
    if not profile or profile.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this student profile")
    stmt = select(StudentActivityLog).where(
        StudentActivityLog.student_profile_id == student_profile_id
    ).order_by(desc(StudentActivityLog.created_at))
    logs = (await db.execute(stmt)).scalars().all()
    
    insights = {
        "math": "Pending Academic Scan...",
        "english": "Pending Academic Scan...",
        "science": "Pending Academic Scan...",
        "first_strategy": "Pending Academic Scan..."
    }
    
    scan_complete = False
    
    # Process logs to build insights (most recent logs first)
    for log in logs:
        if log.activity_type == "academic_scan_complete" and not scan_complete:
            scan_complete = True
            m_json = log.metadata_json or {}
            insights["math"] = f"Scan Result: Working level established at {m_json.get('level', 'Unknown')}. Primary area for improvement: {m_json.get('gap', 'None')}."
            insights["first_strategy"] = f"Focusing on foundational {m_json.get('gap', 'fundamentals')} to bridge the immediate gap."
            
        elif log.activity_type == "lesson_celebrate" or log.activity_type == "lesson_completed":
            insights["math"] = f"Recent Progression: Successfully demonstrated independent mastery of {log.concept} without external intervention."
            insights["first_strategy"] = f"Expanding scope: Advancing past {log.concept} into complex multi-step scenarios."
            
    return {
        "scan_complete": scan_complete,
        "insights": insights
    }
