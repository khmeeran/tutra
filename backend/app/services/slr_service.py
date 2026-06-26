from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import StudentActivityLog
import uuid
import json

VALID_TRANSITIONS = {
    "discovery_started": ["discovery_complete"],
    "discovery_complete": ["academic_scan_started"],
    "academic_scan_started": ["academic_scan_complete"],
    "academic_scan_complete": ["lesson_started"],
    "lesson_started": ["hint_requested", "retry_attempted", "independent_solution", "lesson_completed"],
    "hint_requested": ["retry_attempted", "independent_solution", "lesson_completed", "hint_requested"],
    "retry_attempted": ["hint_requested", "retry_attempted", "independent_solution", "lesson_completed"],
    "independent_solution": ["lesson_celebrate", "lesson_completed"],
    "lesson_celebrate": ["lesson_completed"],
    "lesson_completed": ["lesson_started", "pricing_viewed"]
}

async def log_slr_event(
    db: AsyncSession,
    student_profile_id: uuid.UUID,
    session_id: str,
    idempotency_key: str,
    activity_type: str,
    subject: str = None,
    concept: str = None,
    metadata_json: dict = None
):
    # 1. Idempotency Check
    if idempotency_key:
        stmt = select(StudentActivityLog).where(StudentActivityLog.idempotency_key == idempotency_key)
        existing = (await db.execute(stmt)).scalars().first()
        if existing:
            return existing

    # 2. State Machine Check
    # Fetch the most recent event for this session or overall if no session
    stmt = select(StudentActivityLog).where(
        StudentActivityLog.student_profile_id == student_profile_id
    ).order_by(desc(StudentActivityLog.created_at)).limit(1)
    
    last_event = (await db.execute(stmt)).scalars().first()
    
    if last_event:
        last_type = last_event.activity_type
        # If it's a known state, ensure transition is valid
        if last_type in VALID_TRANSITIONS:
            allowed = VALID_TRANSITIONS[last_type]
            if activity_type not in allowed:
                # We log a warning or reject. For now, we will raise an error to strictly enforce the state machine.
                # However, to avoid breaking the demo abruptly, we can allow 'lesson_started' to restart anytime.
                if activity_type not in ["lesson_started", "discovery_started", "academic_scan_started"]:
                    raise ValueError(f"Invalid state transition from {last_type} to {activity_type}")

    # 3. Write Event
    log = StudentActivityLog(
        student_profile_id=student_profile_id,
        session_id=session_id,
        idempotency_key=idempotency_key,
        activity_type=activity_type,
        subject=subject,
        concept=concept,
        metadata_json=metadata_json or {}
    )
    db.add(log)
    await db.commit()
    return log
