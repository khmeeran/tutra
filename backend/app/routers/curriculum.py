import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Board, Grade, Subject

router = APIRouter(prefix="/api/v1/curriculum", tags=["Curriculum"])

@router.get("/boards")
async def get_boards(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Board))
    return res.scalars().all()

@router.get("/grades/{board_id}")
async def get_grades(board_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Grade).where(Grade.board_id == board_id))
    return res.scalars().all()

@router.get("/subjects/{grade_id}")
async def get_subjects(grade_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Subject).where(Subject.grade_id == grade_id))
    return res.scalars().all()

@router.get("/chapters/{subject_id}")
async def get_chapters(subject_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Chapter).where(Chapter.subject_id == subject_id))
    return res.scalars().all()

@router.get("/topics/{chapter_id}")
async def get_topics(chapter_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Topic).where(Topic.chapter_id == chapter_id).order_by(Topic.sequence_order))
    return res.scalars().all()
