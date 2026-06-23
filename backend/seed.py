import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.models import Board, Grade, Subject

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5433/tutra"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed():
    async with AsyncSessionLocal() as db:
        print("Seeding boards...")
        cbse = Board(name="Central Board of Secondary Education", code="CBSE")
        db.add(cbse)
        await db.flush()
        
        print("Seeding grades...")
        g10 = Grade(board_id=cbse.id, grade_number=10, display_name="Class 10")
        db.add(g10)
        await db.flush()
        
        print("Seeding subjects...")
        math = Subject(grade_id=g10.id, name="Mathematics", code="MATH10", academic_year="2024-25")
        sci = Subject(grade_id=g10.id, name="Science", code="SCI10", academic_year="2024-25")
        db.add_all([math, sci])
        
        await db.commit()
        print("Seed completed! Added CBSE, Class 10, Math, Science.")

if __name__ == "__main__":
    asyncio.run(seed())
