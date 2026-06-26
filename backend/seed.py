import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.models import Board, Grade, Subject, Concept, ConceptDependency

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
        g8 = Grade(board_id=cbse.id, grade_number=8, display_name="Class 8")
        db.add(g8)
        await db.flush()
        
        print("Seeding subjects...")
        math = Subject(grade_id=g8.id, name="Mathematics", code="MATH8", academic_year="2024-25")
        sci = Subject(grade_id=g8.id, name="Science", code="SCI8", academic_year="2024-25")
        db.add_all([math, sci])
        await db.flush()

        print("Seeding Concept Graph for Mathematics...")
        # Prerequisites
        integers = Concept(subject_id=math.id, name="Integers", description="Positive and negative numbers and their operations.")
        fractions = Concept(subject_id=math.id, name="Fractions", description="Parts of a whole and rational numbers.")
        db.add_all([integers, fractions])
        await db.flush()

        # Advanced Concepts
        percentages = Concept(subject_id=math.id, name="Percentages", description="Fractions of 100.")
        algebra_foundations = Concept(subject_id=math.id, name="Algebra Foundations", description="Introduction to variables and basic equations.")
        db.add_all([percentages, algebra_foundations])
        await db.flush()

        # Dependencies
        dep1 = ConceptDependency(concept_id=percentages.id, prerequisite_id=fractions.id)
        dep2 = ConceptDependency(concept_id=algebra_foundations.id, prerequisite_id=integers.id)
        db.add_all([dep1, dep2])
        
        await db.commit()
        print("Seed completed! Added CBSE, Class 8, Math, Science, and Concept Graph.")

if __name__ == "__main__":
    asyncio.run(seed())
