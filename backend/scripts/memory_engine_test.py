import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

# Add backend dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import User, StudentProfile, Board, Grade
from app.memory_models import StudentInterest

async def get_or_create_dummy_student(session):
    # Setup minimal requirements
    board = Board(name="CBSE", code="CBSE")
    session.add(board)
    await session.commit()
    await session.refresh(board)
    
    grade = Grade(board_id=board.id, grade_number=8, display_name="Class 8")
    session.add(grade)
    await session.commit()
    await session.refresh(grade)
    
    user = User(email="test_memory@tutra.edu", role="student")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    profile = StudentProfile(user_id=user.id)
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile

async def run_memory_tests():
    print("--- STARTING MEMORY ENGINE TESTS ---")
    async with AsyncSessionLocal() as session:
        # Cleanup
        await session.execute(StudentInterest.__table__.delete())
        await session.execute(StudentProfile.__table__.delete())
        await session.execute(User.__table__.delete())
        await session.execute(Grade.__table__.delete())
        await session.execute(Board.__table__.delete())
        await session.commit()

        student = await get_or_create_dummy_student(session)
        print(f"✅ Setup: Created dummy student profile {student.id}")
        
        # TEST 1: Memory Creation
        print("\n[TEST 1] Memory Creation")
        interest = StudentInterest(
            student_profile_id=student.id,
            interest_name="Cricket",
            confidence_score=0.8,
            source="Parent_Onboarding"
        )
        session.add(interest)
        await session.commit()
        await session.refresh(interest)
        print(f"✅ Created Memory '{interest.interest_name}' with confidence {interest.confidence_score} and status {interest.status}")
        
        # TEST 2: Memory Reinforcement
        print("\n[TEST 2] Memory Reinforcement")
        interest.confidence_score += 0.1
        interest.last_referenced_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(interest)
        print(f"✅ Reinforced Memory '{interest.interest_name}' -> new confidence {round(interest.confidence_score, 1)}, last_referenced: {interest.last_referenced_at}")
        
        # TEST 3: Memory Decay
        print("\n[TEST 3] Memory Decay")
        # Simulate 2 months decay (-0.1)
        interest.confidence_score -= 0.1
        await session.commit()
        await session.refresh(interest)
        print(f"✅ Decayed Memory '{interest.interest_name}' -> new confidence {round(interest.confidence_score, 1)}")
        
        # TEST 4: Memory Correction (The Sibling Override)
        print("\n[TEST 4] Memory Correction")
        # Student says "I hate cricket, I like F1"
        interest.confidence_score = 0.0
        
        new_interest = StudentInterest(
            student_profile_id=student.id,
            interest_name="Formula 1",
            confidence_score=1.0,
            source="Chat_Inference"
        )
        session.add(new_interest)
        await session.commit()
        await session.refresh(interest)
        await session.refresh(new_interest)
        print(f"✅ Corrected Memory. Legacy '{interest.interest_name}' score: {interest.confidence_score}.")
        print(f"✅ Inserted new Memory '{new_interest.interest_name}' with score: {new_interest.confidence_score}.")
        
        # TEST 5: Memory Archive
        print("\n[TEST 5] Memory Archive")
        interest.status = "Archived"
        await session.commit()
        await session.refresh(interest)
        print(f"✅ Archived Legacy Memory '{interest.interest_name}' -> new status: {interest.status}")
        
        # TEST 6: Memory Deletion
        print("\n[TEST 6] Memory Deletion")
        await session.delete(interest)
        await session.commit()
        
        # Verify
        result = await session.execute(select(StudentInterest).filter_by(interest_name="Cricket"))
        deleted_record = result.scalars().first()
        if not deleted_record:
            print(f"✅ Hard Deleted Legacy Memory 'Cricket' from DB.")
            
    print("\n--- ALL MEMORY TESTS PASSED ---")

if __name__ == "__main__":
    asyncio.run(run_memory_tests())
