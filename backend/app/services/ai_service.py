import json
import ollama
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Topic

async def generate_chat_response(messages_history: list, new_message: str):
    """Generates a chat response using local Ollama model."""
    ollama_messages = [{"role": "system", "content": "You are Tutra, an AI Tutor. Keep answers encouraging, educational, and concise."}]
    for msg in messages_history[-10:]:  # Keep last 10 messages for context
        ollama_messages.append({"role": msg.role, "content": msg.content})
    ollama_messages.append({"role": "user", "content": new_message})
    
    response = ollama.chat(model='llama3', messages=ollama_messages)
    return response['message']['content']

async def generate_quiz_for_topic(db: AsyncSession, topic_id: str, difficulty: str):
    """Generates a 5-question JSON quiz using Ollama."""
    stmt = select(Topic).where(Topic.id == topic_id)
    res = await db.execute(stmt)
    topic = res.scalars().first()
    
    if not topic:
        raise ValueError("Topic not found")

    prompt = f"""Generate a 5-question multiple choice quiz on the topic: {topic.title}. 
Difficulty: {difficulty}. 
Return ONLY valid JSON in this exact format:
[
  {{
    "question": "text",
    "options": ["A", "B", "C", "D"],
    "answer": "A",
    "explanation": "Why A is correct"
  }}
]
"""
    response = ollama.chat(model='llama3', messages=[{"role": "user", "content": prompt}], format="json")
    try:
        quiz_data = json.loads(response['message']['content'])
        return quiz_data
    except json.JSONDecodeError:
        raise ValueError("Failed to generate valid quiz JSON from AI")
