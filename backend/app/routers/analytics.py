import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import TopicMastery, Topic, StudentActivityLog

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@router.get("/progress/{student_profile_id}")
async def get_progress(student_profile_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(TopicMastery, Topic).join(Topic, TopicMastery.topic_id == Topic.id).where(TopicMastery.student_profile_id == student_profile_id)
    res = await db.execute(stmt)
    records = res.all()
    
    progress = []
    for mastery, topic in records:
        progress.append({
            "topic_id": topic.id,
            "topic_title": topic.title,
            "mastery_score": mastery.mastery_score,
            "attempts": mastery.attempts
        })
        
    return {"progress": progress}

@router.get("/activity/{student_profile_id}")
async def get_activity(student_profile_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(StudentActivityLog).where(StudentActivityLog.student_profile_id == student_profile_id).order_by(StudentActivityLog.created_at.desc()).limit(20)
    res = await db.execute(stmt)
    logs = res.scalars().all()
    return logs
