import asyncio
import json
import sys
import os

# Add parent dir to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.models import Base, Topic
from app.database import DATABASE_URL

# Import the new standalone module
from app.intelligence_models import (
    Concept, LearningObjective, Explanation, 
    Misconception, Prerequisite, QuestionBank
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed_intelligence():
    async with engine.begin() as conn:
        print("Ensuring intelligence tables exist via models...")
        # Bind the intelligence models to the same metadata base
        import app.intelligence_models
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        print("Seeding Intelligence Graph for a sample topic...")
        
        # Grab any topic to act as the anchor
        result = await session.execute(select(Topic).limit(1))
        anchor_topic = result.scalars().first()
        
        if not anchor_topic:
            print("No topics found in the database. Please run curriculum ingestion first.")
            return

        print(f"Hooking into Topic ID: {anchor_topic.id}")

        # Seed Concept
        concept = Concept(
            topic_id=anchor_topic.id,
            name="The Breakdown of Glucose by Various Pathways",
            sequence_order=1,
            importance_weight=1.0
        )
        session.add(concept)
        await session.flush()

        # Seed Misconception
        misc = Misconception(
            concept_id=concept.id,
            statement="Respiration and breathing are the exact same thing.",
            correction="Breathing is physical, respiration is chemical breakdown of glucose."
        )
        session.add(misc)
        
        # Seed Learning Objective
        lo = LearningObjective(
            concept_id=concept.id,
            objective_text="Illustrate the 3 pathways of pyruvate breakdown.",
            blooms_taxonomy="Apply"
        )
        session.add(lo)
        await session.flush()

        # Seed Explanation
        exp = Explanation(
            objective_id=lo.id,
            learning_style="Analogical",
            content_markdown="Think of glucose as a large log of wood. Aerobic respiration burns it completely..."
        )
        session.add(exp)

        # Seed Question Bank
        qb = QuestionBank(
            objective_id=lo.id,
            question_type="Multiple Choice",
            difficulty="Medium",
            question_json={"text": "During heavy exercise, cramps occur due to:"},
            correct_answer_json={"answer": "Lactic acid accumulation"},
            explanation_markdown="Lack of oxygen forces anaerobic respiration in muscle cells."
        )
        session.add(qb)

        await session.commit()
        print("Successfully seeded the intelligence graph!")

if __name__ == "__main__":
    asyncio.run(seed_intelligence())
