import json
import ollama
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Concept
import time
from datetime import datetime
import os

def log_test_sprint(event_type, data):
    log_file = "E:/Tutra/lesson_test_sprint.jsonl"
    entry = {"timestamp": datetime.now().isoformat(), "event_type": event_type, "data": data}
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


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


async def generate_discovery_reflection(history: list, answer: str):
    """Generates a deeply empathetic reflection AND dynamically generates the next follow-up question."""
    
    current_question = ""
    for msg in reversed(history):
        if msg["role"] == "assistant":
            current_question = msg["content"]
            break

    prompt = f"""You are Tutra's Discovery Engine. You are a quiet, empathetic companion listening to a parent.
The parent just answered this question: "{current_question}"
Their answer is: "{answer}"

Rule 1: Write a short, 1-2 sentence REFLECTION that shows deep listening. Never start with "I understand" or "That makes sense".
Rule 2: Do NOT give advice or diagnose.
Rule 3: Write the NEXT QUESTION to ask the parent. The question should dig deeper based on their answer. Make it profound, curious, and open-ended.
Rule 4: You must return ONLY valid JSON in the exact format:
{{
  "reflection": "Your empathetic reflection here.",
  "next_question": "Your next follow-up question here."
}}
"""
    
    messages = [{"role": "system", "content": "You are a quiet, empathetic listener. Always output valid JSON."}]
    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})

    start_time = time.time()
    response = ollama.chat(model='llama3', messages=messages, format="json")
    duration = time.time() - start_time

    try:
        data = json.loads(response['message']['content'])
        return data
    except json.JSONDecodeError:
        return {
            "reflection": "Thank you for sharing that.",
            "next_question": "Can you tell me more about what makes them unique?"
        }

async def generate_discovery_report(history: list):
    """Generates deep, synthesized insights from the discovery conversation."""
    convo_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history])
    
    prompt = f"""You are Tutra's Intelligence Engine. A parent just completed a discovery flow for their child.
Your job is NOT to summarize. Do NOT repeat what the parent typed. 
You are a pattern detector. Generate deep insights based on Observation + Connection + Implication.
Every insight MUST make the parent think: 'Hmm... I never thought about it that way.'

Generate 4 insights mapping to these cards:
1. "engagement": What may be driving engagement. (Look past the obvious interests. E.g. if they like gaming, they like immediate feedback and visible progress).
2. "confidence": Where confidence might be leaking. (Look past the explicit worries. E.g. focus might drop only when rewards are delayed, suggesting a motivation issue, not an attention issue).
3. "strength": A strength we think is being overlooked. (A positive reframe of a negative, or an unexpected synergy).
4. "first_win": The first win we'd create. (A highly specific, actionable first session idea that avoids their fear and leverages their interest).

Return ONLY valid JSON in this exact format:
{{
  "engagement": "deep insight here...",
  "confidence": "deep insight here...",
  "strength": "deep insight here...",
  "first_win": "deep insight here..."
}}

Conversation:
{convo_text}
"""
    response = ollama.chat(model='llama3', messages=[{"role": "user", "content": prompt}], format="json")
    try:
        data = json.loads(response['message']['content'])
        return data
    except json.JSONDecodeError:
        return {
            "engagement": "We noticed a pattern in how they interact with challenges. Activities they enjoy seem to share a need for autonomy and clear feedback.",
            "confidence": "Confidence appears to waver not when the task is hard, but when the instructions are ambiguous.",
            "strength": "Their tendency to shift focus rapidly is often framed as a negative, but it indicates a highly dynamic mind seeking optimal stimulation.",
            "first_win": "We would start with a highly visual, no-stakes puzzle that offers immediate feedback to build momentum before introducing any formal instruction."
        }

async def generate_math_scan(history: list, student_data: dict = None):
    """Dynamically powers the Math Academic Scan. Asks adaptive questions or finalizes."""
    if student_data is None:
        student_data = {}
        
    student_class = student_data.get("class", "8")
    try:
        student_class_num = int(str(student_class).replace("Class ", "").strip())
    except ValueError:
        student_class_num = 8
        
    target_class = max(1, student_class_num - 1)
    board = student_data.get("board", "CBSE")
    
    # Count how many questions the assistant has asked so far.
    assistant_msgs = [m for m in history if m['role'] == 'assistant']
    
    # Target: Evaluate after ~4 questions.
    if len(assistant_msgs) >= 4:
        convo_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history])
        prompt = f"""You are Tutra's Academic Engine (Curriculum-Aware Diagnostic Engine).
Analyze the following math interaction with a student (Class {student_class}, Board: {board}).
Determine their mastery of concepts from the target curriculum (Class {target_class}).

Return ONLY valid JSON in this exact format:
{{
  "complete": true,
  "level": "Class {target_class} Mid-Year",
  "gap": "Word problems",
  "strength": "Percentages"
}}

Interaction:
{convo_text}
"""
        log_test_sprint("academic_scan_prompt", {"prompt": prompt, "history": history})
        response = ollama.chat(model='llama3', messages=[{"role": "user", "content": prompt}], format="json")
        log_test_sprint("academic_scan_response", {"response": response['message']['content']})
        try:
            return json.loads(response['message']['content'])
        except json.JSONDecodeError:
            return {"complete": True, "level": f"Class {target_class}", "gap": "Unknown", "strength": "Unknown"}
    
    else:
        convo_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history])
        prompt = f"""You are Tutra's Adaptive Math Engine. You are scanning a student's math reasoning ability.
Student Profile: Class {student_class}, Board: {board}.
Target Curriculum: Class {target_class} concepts (e.g., Fractions, Decimals, Percentages, Ratio, Algebra).

Rules:
1. Provide a stealth assessment: hide the math inside an engaging puzzle or activity. 
2. Use Indian context (Rupees, cricket, school, shops). DO NOT use miles, gallons, dollars.
3. Keep it to one concept per question, max 2 lines. Focus on the core math concept.
4. If they got the last one right, move to a new concept or a slightly harder application.
5. If they struggled, drill down to a simpler diagnostic step.
6. Act like a friendly mentor, not an exam proctor. "Play -> Think -> Solve -> Learn"

Return ONLY valid JSON in this exact format:
{{
  "complete": false,
  "question": "Your next math question here."
}}
"""
        if history:
            prompt += f"\nConversation:\n{convo_text}"
            log_test_sprint("student_response", {"message": history[-1]["content"] if history else ""})
        else:
            prompt += f"\nGenerate the FIRST engaging math puzzle to test a Class {target_class} concept."
            
        log_test_sprint("academic_scan_prompt", {"prompt": prompt})
        response = ollama.chat(model='llama3', messages=[{"role": "user", "content": prompt}], format="json")
        log_test_sprint("academic_scan_response", {"response": response['message']['content']})
        try:
            return json.loads(response['message']['content'])
        except json.JSONDecodeError:
            return {"complete": False, "question": "Let's calculate something fun. If you have ₹500 and spend 20% on a cricket bat, how much is left?"}

async def generate_lesson_step(history: list, concept: str):
    """Dynamically generates the next step in a stealth lesson."""
    prompt = f"""You are Tutra's Stealth Lesson Engine. You are teaching a student about "{concept}".
Your philosophy: "Play -> Think -> Solve -> Learn".
Do not lecture. Ask an engaging question or provide a tiny puzzle.
Use Indian context (Rupees, cricket, school).
If the student struggles, break it down. If they get it, advance to a harder application.

Analyze the conversation history. Decide the next state of the lesson.
States:
- "teach": Continue the dialogue, ask the next micro-question.
- "wait": If they just solved a core conceptual hurdle, tell them they did great and we are taking a pause.
- "retest": Give them a slightly harder, applied question to prove mastery.
- "celebrate": If they passed the retest independently, celebrate their win so we can exit the lesson.

Return ONLY valid JSON in this exact format:
{{
  "state": "teach",
  "message": "Your next message to the student here."
}}
"""
    convo_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history])
    if convo_text:
        prompt += f"\nConversation:\n{convo_text}"
        log_test_sprint("student_response", {"message": history[-1]["content"] if history else ""})
    else:
        prompt += f"\nGenerate the opening message for this stealth lesson."
        
    log_test_sprint("lesson_prompt", {"prompt": prompt})
    response = ollama.chat(model='llama3', messages=[{"role": "user", "content": prompt}], format="json")
    log_test_sprint("lesson_response", {"response": response['message']['content']})
    
    try:
        data = json.loads(response['message']['content'])
        if data.get("state") not in ["teach", "wait", "retest", "celebrate"]:
            data["state"] = "teach"
        log_test_sprint("state_transition", {"state": data["state"], "message": data.get("message", "")})
        return data
    except json.JSONDecodeError:
        return {
            "state": "teach",
            "message": "Let's try looking at this from another angle."
        }

