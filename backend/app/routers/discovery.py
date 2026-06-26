from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.ai_service import generate_discovery_reflection, generate_discovery_report, generate_math_scan
from app.auth import get_current_user
from app.models import User, StudentProfile
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.slr_service import log_slr_event
import uuid

router = APIRouter(prefix="/api/v1/discovery", tags=["Discovery"])

class ReflectionRequest(BaseModel):
    history: List[Dict[str, str]]
    answer: str

class ReportRequest(BaseModel):
    history: List[Dict[str, str]]
    student_profile_id: uuid.UUID
    session_id: str
    idempotency_key: str

class ScanRequest(BaseModel):
    history: List[Dict[str, str]]
    student_data: Dict[str, Any] = {}
    student_profile_id: uuid.UUID
    session_id: str
    idempotency_key: str

@router.post("/reflect")
async def get_reflection(data: ReflectionRequest, user: User = Depends(get_current_user)):
    """Generates an empathetic reflection and the NEXT question."""
    try:
        result = await generate_discovery_reflection(data.history, data.answer)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
async def get_report(data: ReportRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Generates the final Discovery Report and logs it to SLR."""
    try:
        report = await generate_discovery_report(data.history)
        
        await log_slr_event(
            db=db,
            student_profile_id=data.student_profile_id,
            session_id=data.session_id,
            idempotency_key=data.idempotency_key,
            activity_type="discovery_complete",
            subject="General",
            concept="Discovery",
            metadata_json=report
        )
        
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/math-scan")
async def get_math_scan(data: ScanRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Generates the next adaptive math question or completes the scan and logs to SLR."""
    try:
        # First, log scan started if this is the first question
        if len(data.history) <= 1:
            await log_slr_event(
                db=db,
                student_profile_id=data.student_profile_id,
                session_id=data.session_id,
                idempotency_key=data.idempotency_key + "_started",
                activity_type="academic_scan_started",
                subject="Mathematics",
                concept="General",
                metadata_json={}
            )
            
        result = await generate_math_scan(data.history, data.student_data)
        
        if result.get("complete"):
            await log_slr_event(
                db=db,
                student_profile_id=data.student_profile_id,
                session_id=data.session_id,
                idempotency_key=data.idempotency_key + "_complete",
                activity_type="academic_scan_complete",
                subject="Mathematics",
                concept=result.get("gap", "General"),
                metadata_json={
                    "level": result.get("level"),
                    "gap": result.get("gap"),
                    "strength": result.get("strength")
                }
            )
            
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
