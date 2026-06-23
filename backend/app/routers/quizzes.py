import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Dict
from app.database import get_db
from app.models import Quiz, QuizQuestion, QuizAttempt, TopicMastery, Topic, StudentActivityLog
from app.services.ai_service import generate_quiz_for_topic

router = APIRouter(prefix="/api/v1/quizzes", tags=["Quizzes"])

class GenerateQuizReq(BaseModel):
    topic_id: uuid.UUID
    difficulty: str = "medium"

class SubmitQuizReq(BaseModel):
    answers: Dict[str, str]  # question_id -> answer

@router.post("/generate")
async def generate_quiz(req: GenerateQuizReq, db: AsyncSession = Depends(get_db)):
    # Assuming user is authenticated and student_profile_id is known. Hardcoding for MVP.
    student_profile_id = uuid.UUID("00000000-0000-0000-0000-000000000000") # placeholder
    
    # 1. Fetch topic to get chapter/subject context
    stmt = select(Topic).where(Topic.id == req.topic_id)
    topic = (await db.execute(stmt)).scalars().first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # 2. Call AI
    try:
        quiz_data = await generate_quiz_for_topic(db, req.topic_id, req.difficulty)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 3. Create Quiz
    quiz = Quiz(
        student_profile_id=student_profile_id,
        subject_id=uuid.uuid4(), # placeholder, should map from topic->chapter->subject
        chapter_id=topic.chapter_id,
        difficulty=req.difficulty,
        generated_by="ai"
    )
    db.add(quiz)
    await db.flush()

    # 4. Create Questions
    for q in quiz_data:
        qq = QuizQuestion(
            quiz_id=quiz.id,
            question_text=q['question'],
            question_type="mcq",
            options_json=q['options'],
            correct_answer=q['answer'],
            explanation=q.get('explanation', '')
        )
        db.add(qq)
    
    await db.commit()
    return {"quiz_id": quiz.id, "questions": quiz_data}

@router.post("/{quiz_id}/submit")
async def submit_quiz(quiz_id: uuid.UUID, req: SubmitQuizReq, db: AsyncSession = Depends(get_db)):
    student_profile_id = uuid.UUID("00000000-0000-0000-0000-000000000000") # placeholder
    
    # Evaluate answers
    stmt = select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id)
    questions = (await db.execute(stmt)).scalars().all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    correct = 0
    total = len(questions)
    
    for q in questions:
        ans = req.answers.get(str(q.id))
        if ans and ans.strip().lower() == q.correct_answer.strip().lower():
            correct += 1
            
    score = correct
    percentage = (correct / total) * 100 if total > 0 else 0
    
    # Save attempt
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_profile_id=student_profile_id,
        score=score,
        percentage=percentage,
        answers_json=req.answers
    )
    db.add(attempt)
    
    # Update mastery (simplified)
    # Fetch quiz to get topic -> chapter -> subject (omitted for brevity, assume topic_id is known)
    # Log activity
    log = StudentActivityLog(
        student_profile_id=student_profile_id,
        activity_type="quiz_submitted",
        metadata_json={"quiz_id": str(quiz_id), "score": percentage}
    )
    db.add(log)
    
    await db.commit()
    return {"score": score, "percentage": percentage}
