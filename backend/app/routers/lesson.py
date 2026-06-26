from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.ai_service import generate_lesson_step
from app.auth import get_current_user
from app.models import User
from fastapi import Depends
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.slr_service import log_slr_event
import uuid

router = APIRouter(prefix="/api/v1/lesson", tags=["Lesson"])

class LessonRequest(BaseModel):
    history: List[Dict[str, str]]
    concept: str
    student_profile_id: uuid.UUID
    session_id: str
    idempotency_key: str

@router.post("/next-step")
async def get_next_step(data: LessonRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Generates the next step in the dynamic stealth lesson."""
    try:
        # Determine current state based on history
        # If history is empty, this is the start of a lesson
        if len(data.history) == 0:
            await log_slr_event(
                db=db,
                student_profile_id=data.student_profile_id,
                session_id=data.session_id,
                idempotency_key=data.idempotency_key + "_start",
                activity_type="lesson_started",
                subject="Mathematics",
                concept=data.concept,
                metadata_json={}
            )
        else:
            # We assume user just answered. In a real system, we'd analyze if it was a retry, hint request, or independent solution.
            # Here we just log an interaction event.
            await log_slr_event(
                db=db,
                student_profile_id=data.student_profile_id,
                session_id=data.session_id,
                idempotency_key=data.idempotency_key + f"_interaction_{len(data.history)}",
                activity_type="retry_attempted", # Simplification: Treat all subsequent interactions as retries
                subject="Mathematics",
                concept=data.concept,
                metadata_json={"history_length": len(data.history)}
            )

        result = await generate_lesson_step(data.history, data.concept)
        
        # Determine if we reached celebrate/wait state
        if result.get("state") == "celebrate":
            await log_slr_event(
                db=db,
                student_profile_id=data.student_profile_id,
                session_id=data.session_id,
                idempotency_key=data.idempotency_key + "_celebrate",
                activity_type="lesson_celebrate",
                subject="Mathematics",
                concept=data.concept,
                metadata_json={"status": "independent_mastery"}
            )
            
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
