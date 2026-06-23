from datetime import date, datetime
from typing import Optional, Any
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime, Date, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import uuid

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class Organization(Base, TimestampMixin):
    __tablename__ = 'organizations'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default='active')

class User(Base, TimestampMixin):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default='active')
    auth_provider: Mapped[str] = mapped_column(String(50), default='local')

class OrganizationUser(Base, TimestampMixin):
    __tablename__ = 'organization_users'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('organizations.id', ondelete='CASCADE'))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    role: Mapped[str] = mapped_column(String(50))
    __table_args__ = (UniqueConstraint('organization_id', 'user_id'),)

class ParentStudentMap(Base, TimestampMixin):
    __tablename__ = 'parent_student_map'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    student_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    relationship: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    __table_args__ = (UniqueConstraint('parent_user_id', 'student_user_id'),)

class StudentProfile(Base, TimestampMixin):
    __tablename__ = 'student_profiles'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    medium: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    school_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

class Board(Base, TimestampMixin):
    __tablename__ = 'boards'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(100), unique=True)

class Grade(Base, TimestampMixin):
    __tablename__ = 'grades'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('boards.id', ondelete='CASCADE'))
    grade_number: Mapped[int] = mapped_column(Integer)
    display_name: Mapped[str] = mapped_column(String(100))
    __table_args__ = (UniqueConstraint('board_id', 'grade_number'),)

class Enrollment(Base, TimestampMixin):
    __tablename__ = 'enrollments'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    grade_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('grades.id', ondelete='CASCADE'))
    academic_year: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default='active')
    __table_args__ = (UniqueConstraint('student_profile_id', 'grade_id', 'academic_year'),)

class Subject(Base, TimestampMixin):
    __tablename__ = 'subjects'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grade_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('grades.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(100))
    academic_year: Mapped[str] = mapped_column(String(50))
    __table_args__ = (UniqueConstraint('grade_id', 'code', 'academic_year'),)

class StudentSubject(Base, TimestampMixin):
    __tablename__ = 'student_subjects'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enrollment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('enrollments.id', ondelete='CASCADE'))
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('subjects.id', ondelete='CASCADE'))
    status: Mapped[str] = mapped_column(String(50), default='active')
    __table_args__ = (UniqueConstraint('enrollment_id', 'subject_id'),)

class Chapter(Base, TimestampMixin):
    __tablename__ = 'chapters'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('subjects.id', ondelete='CASCADE'))
    chapter_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class Topic(Base, TimestampMixin):
    __tablename__ = 'topics'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('chapters.id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(String(255))
    sequence_order: Mapped[int] = mapped_column(Integer)

class LearningContent(Base, TimestampMixin):
    __tablename__ = 'learning_content'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('topics.id', ondelete='CASCADE'))
    content_type: Mapped[str] = mapped_column(String(100))
    language: Mapped[str] = mapped_column(String(50), default='en')
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(50), default='1.0')

class Conversation(Base, TimestampMixin):
    __tablename__ = 'conversations'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('subjects.id', ondelete='CASCADE'))
    chapter_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('chapters.id', ondelete='SET NULL'), nullable=True)
    topic_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('topics.id', ondelete='SET NULL'), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='active')

class Message(Base, TimestampMixin):
    __tablename__ = 'messages'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('conversations.id', ondelete='CASCADE'))
    role: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    metadata_json: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)

class Quiz(Base, TimestampMixin):
    __tablename__ = 'quizzes'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('subjects.id', ondelete='CASCADE'))
    chapter_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('chapters.id', ondelete='SET NULL'), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    generated_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

class QuizQuestion(Base, TimestampMixin):
    __tablename__ = 'quiz_questions'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('quizzes.id', ondelete='CASCADE'))
    question_text: Mapped[str] = mapped_column(Text)
    question_type: Mapped[str] = mapped_column(String(100))
    options_json: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    marks: Mapped[Optional[int]] = mapped_column(Integer, default=1)

class QuizAttempt(Base, TimestampMixin):
    __tablename__ = 'quiz_attempts'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('quizzes.id', ondelete='CASCADE'))
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    answers_json: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class TopicMastery(Base, TimestampMixin):
    __tablename__ = 'topic_mastery'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('topics.id', ondelete='CASCADE'))
    mastery_score: Mapped[Optional[float]] = mapped_column(Float, default=0)
    attempts: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    __table_args__ = (UniqueConstraint('student_profile_id', 'topic_id'),)

class StudentActivityLog(Base):
    __tablename__ = 'student_activity_log'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    activity_type: Mapped[str] = mapped_column(String(100))
    metadata_json: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Plan(Base, TimestampMixin):
    __tablename__ = 'plans'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    monthly_price: Mapped[float] = mapped_column(Float)
    yearly_price: Mapped[float] = mapped_column(Float)
    gateway_product_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class Subscription(Base, TimestampMixin):
    __tablename__ = 'subscriptions'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('organizations.id', ondelete='CASCADE'))
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('plans.id', ondelete='RESTRICT'))
    status: Mapped[str] = mapped_column(String(50), default='active')
    gateway_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    renewal_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class Payment(Base, TimestampMixin):
    __tablename__ = 'payments'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('subscriptions.id', ondelete='CASCADE'))
    gateway: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default='INR')
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    transaction_reference: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
