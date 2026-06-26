import uuid
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .database import engine, get_db
from . import schemas, auth
from .routers import curriculum, quizzes, analytics, discovery, lesson, learning_record, auth as auth_router
from .services.ai_service import generate_chat_response

from app.models import Base, User, Organization, OrganizationUser, StudentProfile, Enrollment, Conversation, Message, Plan, Subscription

app = FastAPI(title="Tutra Full MVP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

app.include_router(curriculum.router)
app.include_router(quizzes.router)
app.include_router(analytics.router)
app.include_router(discovery.router)
app.include_router(lesson.router)
app.include_router(learning_record.router)
app.include_router(auth_router.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Ensure Free Plan exists
    async with AsyncSession(engine) as db:
        res = await db.execute(select(Plan).where(Plan.name == "Free"))
        if not res.scalars().first():
            db.add(Plan(name="Free", monthly_price=0.0, yearly_price=0.0))
            await db.commit()

@app.post("/api/v1/auth/register/parent", response_model=schemas.Token, tags=["Auth"])
async def register_parent(data: schemas.ParentRegister, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where((User.email == data.email) | (User.phone == data.phone))
    if (await db.execute(stmt)).scalars().first():
        raise HTTPException(status_code=400, detail="User already exists")
    
    org = Organization(name=f"{data.name}'s Family", type="family")
    db.add(org)
    await db.flush()
    
    user = User(email=data.email, phone=data.phone, password_hash=auth.get_password_hash(data.password), role="parent")
    db.add(user)
    await db.flush()
    
    db.add(OrganizationUser(organization_id=org.id, user_id=user.id, role="admin"))
    
    # Assign Free Subscription
    plan = (await db.execute(select(Plan).where(Plan.name == "Free"))).scalars().first()
    if plan:
        db.add(Subscription(organization_id=org.id, plan_id=plan.id, status="active"))
        
    await db.commit()
    return {"access_token": auth.create_access_token({"sub": str(user.id), "role": user.role}), "token_type": "bearer"}

@app.post("/api/v1/auth/login", response_model=schemas.Token, tags=["Auth"])
async def login(data: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where((User.email == data.identifier) | (User.phone == data.identifier)))).scalars().first()
    if not user or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": auth.create_access_token({"sub": str(user.id), "role": user.role}), "token_type": "bearer"}

@app.post("/api/v1/students", tags=["Students"])
async def create_student(data: schemas.StudentCreate, user: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can create students")
    
    student_user = User(role="student")
    db.add(student_user)
    await db.flush()
    
    profile = StudentProfile(user_id=student_user.id, medium=data.medium, school_name=data.school_name)
    db.add(profile)
    await db.flush()
    
    enrollment = Enrollment(student_profile_id=profile.id, grade_id=data.grade_id, academic_year=data.academic_year)
    db.add(enrollment)
    await db.commit()
    return {"message": "Student created", "student_profile_id": str(profile.id)}

@app.post("/api/v1/conversations/chat", response_model=schemas.ChatResponse, tags=["Chat"])
async def chat(data: schemas.ChatRequest, user: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    profile = (await db.execute(select(StudentProfile).where(StudentProfile.user_id == user.id))).scalars().first()
    if not profile:
        profile = StudentProfile(user_id=user.id, medium="N/A", school_name="Testing")
        db.add(profile)
        await db.flush()
    profile_id = profile.id
        
    conv = (await db.execute(select(Conversation).where(and_(Conversation.student_profile_id == profile_id, Conversation.subject_id == data.subject_id)))).scalars().first()
    
    if not conv:
        conv = Conversation(student_profile_id=profile_id, subject_id=data.subject_id, title="AI Session")
        db.add(conv)
        await db.flush()
        
    # Get history
    history = (await db.execute(select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at))).scalars().all()
    
    user_msg = Message(conversation_id=conv.id, role="user", content=data.message)
    db.add(user_msg)
    await db.flush()
    
    # Generate AI Response
    ai_text = await generate_chat_response(history, data.message)
    
    ai_msg = Message(conversation_id=conv.id, role="assistant", content=ai_text, model_used="llama3")
    db.add(ai_msg)
    await db.commit()
    
    return {"response": ai_text}
