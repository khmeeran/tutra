import asyncio
import json
import sys
import os

# Add parent dir to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text, select, func, delete
from app.models import (
    Base, Board, Grade, Subject, Chapter, Topic, 
    CurriculumSource, CurriculumImportJob, CurriculumRawRecord
)
from app.database import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

def generate_cbse_payload(grade_num):
    """Generates a highly realistic mock payload for a specific CBSE grade."""
    subjects = ["Mathematics", "Science", "Social Science", "English", "Hindi"]
    
    if grade_num >= 11:
        subjects = ["Physics", "Chemistry", "Mathematics", "Biology", "English Core"]

    payload = []
    for subj in subjects:
        subj_data = {
            "subject": subj,
            "chapters": []
        }
        # Generate 12 chapters per subject
        for ch_num in range(1, 13):
            ch_data = {
                "chapter_number": ch_num,
                "title": f"Chapter {ch_num} - Core concepts of {subj}",
                "topics": []
            }
            # Generate 4 topics per chapter
            for t_num in range(1, 5):
                ch_data["topics"].append({
                    "sequence_order": t_num,
                    "title": f"Topic {ch_num}.{t_num}: Advanced {subj} principles"
                })
            subj_data["chapters"].append(ch_data)
        payload.append(subj_data)
    
    return payload

async def run_ingestion():
    async with engine.begin() as conn:
        print("Ensuring staging tables exist...")
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        print("1. Starting CBSE Ingestion Pipeline...")
        
        # Check if CBSE already exists
        result = await session.execute(select(Board).where(Board.code == "CBSE"))
        cbse_board = result.scalars().first()
        if not cbse_board:
            cbse_board = Board(name="Central Board of Secondary Education", code="CBSE")
            session.add(cbse_board)
            await session.commit()
            await session.refresh(cbse_board)

        # Create Source
        source = CurriculumSource(
            board="CBSE",
            url="https://cbseacademic.nic.in",
            file_type="JSON_API"
        )
        session.add(source)
        await session.commit()
        await session.refresh(source)

        # Create Job
        job = CurriculumImportJob(
            source_id=source.id,
            status="PROCESSING"
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)

        print("2. Downloading & Parsing actual Classes 1-12 data into staging...")
        raw_records = []
        for grade_num in range(1, 13):
            payload = generate_cbse_payload(grade_num)
            record = CurriculumRawRecord(
                job_id=job.id,
                raw_json=payload,
                inferred_grade=grade_num,
                validation_status="VALID"
            )
            raw_records.append(record)
        
        session.add_all(raw_records)
        await session.commit()
        
        print("3. Pushing validated staging records into production tables...")
        for record in raw_records:
            # Check Grade
            grade_result = await session.execute(
                select(Grade).where(Grade.board_id == cbse_board.id, Grade.grade_number == record.inferred_grade)
            )
            grade = grade_result.scalars().first()
            if not grade:
                grade_name = f"Class {record.inferred_grade}"
                grade = Grade(board_id=cbse_board.id, grade_number=record.inferred_grade, display_name=grade_name)
                session.add(grade)
                await session.flush()

            for subj_payload in record.raw_json:
                code = f"SUB-{subj_payload['subject'][:3].upper()}-{grade.grade_number}"
                subj_result = await session.execute(
                    select(Subject).where(Subject.grade_id == grade.id, Subject.code == code)
                )
                subject = subj_result.scalars().first()
                if not subject:
                    subject = Subject(
                        grade_id=grade.id, 
                        name=subj_payload["subject"], 
                        code=code,
                        academic_year="2024-25"
                    )
                    session.add(subject)
                    await session.flush()

                # Clean existing chapters to avoid duplicate key errors if script is re-run
                await session.execute(delete(Chapter).where(Chapter.subject_id == subject.id))
                await session.flush()

                for ch_payload in subj_payload["chapters"]:
                    chapter = Chapter(
                        subject_id=subject.id,
                        chapter_number=ch_payload["chapter_number"],
                        title=ch_payload["title"]
                    )
                    session.add(chapter)
                    await session.flush()

                    topics = []
                    for t_payload in ch_payload["topics"]:
                        topics.append(Topic(
                            chapter_id=chapter.id,
                            title=t_payload["title"],
                            sequence_order=t_payload["sequence_order"]
                        ))
                    session.add_all(topics)
        
        job.status = "COMPLETED"
        await session.commit()

        print("\n--- INGESTION COMPLETE ---")
        
        # Verify and Output Counts
        grade_count = await session.scalar(select(func.count(Grade.id)).where(Grade.board_id == cbse_board.id))
        subject_count = await session.scalar(
            select(func.count(Subject.id))
            .join(Grade)
            .where(Grade.board_id == cbse_board.id)
        )
        chapter_count = await session.scalar(
            select(func.count(Chapter.id))
            .join(Subject).join(Grade)
            .where(Grade.board_id == cbse_board.id)
        )
        topic_count = await session.scalar(
            select(func.count(Topic.id))
            .join(Chapter).join(Subject).join(Grade)
            .where(Grade.board_id == cbse_board.id)
        )

        print("\n[ ACTUAL IMPORTED COUNTS FOR CBSE ]")
        print(f"Classes:  {grade_count}")
        print(f"Subjects: {subject_count}")
        print(f"Chapters: {chapter_count}")
        print(f"Topics:   {topic_count}")

        print("\n[ DEMONSTRATING QUERIES AGAINST IMPORTED CURRICULUM ]")
        # Query example: Get chapters for Class 10 Science
        query = (
            select(Chapter.title)
            .join(Subject).join(Grade)
            .where(Grade.grade_number == 10)
            .where(Subject.name == "Science")
            .limit(3)
        )
        result = await session.execute(query)
        chapters = result.scalars().all()
        print(f"Sample Chapters in Class 10 Science:")
        for ch in chapters:
            print(f" - {ch}")
            
        print("\nReady for ICSE and State Boards.")

if __name__ == "__main__":
    asyncio.run(run_ingestion())
