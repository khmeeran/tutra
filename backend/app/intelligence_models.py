from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

# Import core dependencies from the main curriculum module
from app.models import Base, TimestampMixin

class Concept(Base, TimestampMixin):
    __tablename__ = 'concepts'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # FK bridging to the Main Curriculum Schema
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('topics.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(255))
    sequence_order: Mapped[int] = mapped_column(Integer)
    importance_weight: Mapped[float] = mapped_column(Float, default=1.0)

class Prerequisite(Base, TimestampMixin):
    __tablename__ = 'prerequisites'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('concepts.id', ondelete='CASCADE'))
    prerequisite_concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('concepts.id', ondelete='CASCADE'))

class LearningObjective(Base, TimestampMixin):
    __tablename__ = 'learning_objectives'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('concepts.id', ondelete='CASCADE'))
    objective_text: Mapped[str] = mapped_column(Text)
    blooms_taxonomy: Mapped[str] = mapped_column(String(50)) # e.g. Remember, Understand, Apply, Analyze, Evaluate, Create

class Explanation(Base, TimestampMixin):
    __tablename__ = 'explanations'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    objective_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('learning_objectives.id', ondelete='CASCADE'))
    learning_style: Mapped[str] = mapped_column(String(50)) # e.g. Visual, Analogical, Literal
    content_markdown: Mapped[str] = mapped_column(Text)

class Misconception(Base, TimestampMixin):
    __tablename__ = 'misconceptions'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('concepts.id', ondelete='CASCADE'))
    statement: Mapped[str] = mapped_column(Text)
    correction: Mapped[str] = mapped_column(Text)

class QuestionBank(Base, TimestampMixin):
    __tablename__ = 'question_bank'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    objective_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('learning_objectives.id', ondelete='CASCADE'))
    question_type: Mapped[str] = mapped_column(String(100))
    difficulty: Mapped[str] = mapped_column(String(50))
    question_json: Mapped[Any] = mapped_column(JSONB)
    correct_answer_json: Mapped[Any] = mapped_column(JSONB)
    explanation_markdown: Mapped[str] = mapped_column(Text)

class QuizTemplate(Base, TimestampMixin):
    __tablename__ = 'quiz_templates'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    rules_json: Mapped[Any] = mapped_column(JSONB)

class ConceptMastery(Base, TimestampMixin):
    __tablename__ = 'concept_mastery'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # FK bridging to Student Profiles
    student_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('student_profiles.id', ondelete='CASCADE'))
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('concepts.id', ondelete='CASCADE'))
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)
    questions_attempted: Mapped[int] = mapped_column(Integer, default=0)
    last_assessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    decay_factor: Mapped[float] = mapped_column(Float, default=1.0)
