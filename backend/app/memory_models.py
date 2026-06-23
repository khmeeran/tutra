import uuid
from typing import Optional, Any
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models import Base, TimestampMixin

class StudentInterest(Base, TimestampMixin):
    __tablename__ = 'student_interests'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    interest_name: Mapped[str] = mapped_column(String(255))
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped[str] = mapped_column(String(50), default='system')
    last_referenced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='Active')

class StudentLearningPreference(Base, TimestampMixin):
    __tablename__ = 'student_learning_preferences'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    preference_type: Mapped[str] = mapped_column(String(100))
    weight: Mapped[float] = mapped_column(Float, default=1.0)

class StudentEmotionalSignal(Base, TimestampMixin):
    __tablename__ = 'student_emotional_signals'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('concepts.id', ondelete='SET NULL'), nullable=True)
    emotion: Mapped[str] = mapped_column(String(100))
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class StudentRelationshipMemory(Base, TimestampMixin):
    __tablename__ = 'student_relationship_memories'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('concepts.id', ondelete='SET NULL'), nullable=True)
    memory_text: Mapped[str] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    last_referenced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='Active')

class StudentSuccessMoment(Base, TimestampMixin):
    __tablename__ = 'student_success_moments'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('concepts.id', ondelete='SET NULL'), nullable=True)
    milestone_text: Mapped[str] = mapped_column(Text)
    achieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

class StudentMisconceptionHistory(Base, TimestampMixin):
    __tablename__ = 'student_misconception_history'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    misconception_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('misconceptions.id', ondelete='CASCADE'))
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class LearningSession(Base, TimestampMixin):
    __tablename__ = 'learning_sessions'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    session_type: Mapped[str] = mapped_column(String(50))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class SessionEvent(Base, TimestampMixin):
    __tablename__ = 'session_events'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('learning_sessions.id', ondelete='CASCADE'))
    concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('concepts.id', ondelete='SET NULL'), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100))
    metadata_json: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)

class MemoryReference(Base, TimestampMixin):
    __tablename__ = 'memory_references'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('learning_sessions.id', ondelete='CASCADE'))
    relationship_memory_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('student_relationship_memories.id', ondelete='SET NULL'), nullable=True)
    interest_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('student_interests.id', ondelete='SET NULL'), nullable=True)
    referenced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

class Recommendation(Base, TimestampMixin):
    __tablename__ = 'recommendations'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('concepts.id', ondelete='CASCADE'))
    recommendation_type: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default='Pending')
