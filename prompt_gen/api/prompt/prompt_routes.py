from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from prompt_gen.models.orm_models import Prompt, User
from prompt_gen.database.db import SessionLocal
from prompt_gen.models.pydantic_models import PromptCreate, PromptAnswerInput, PromptResponse, PromptUsageStats
from datetime import datetime, timedelta
from typing import List
from pytz import timezone
import requests
import os
from dotenv import load_dotenv

load_dotenv()
AI_URL = os.getenv("OLLAMA_API_URL")
router = APIRouter()
ist = timezone("Asia/Kolkata")
# === DB Dependency ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Ollama LLM Query ===
def query_deepseek_ollama(prompt: str):
    try:
        response = requests.post(AI_URL, json={
            "model": "deepseek-llm:7b",
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print("Error querying Ollama:", e)
        raise HTTPException(status_code=500, detail="Error from local AI model")


# === Route: Generate Questions from Idea ===
@router.post("/idea", response_model=PromptResponse)
def receive_idea(payload: PromptCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.gmail_id == payload.gmail_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prompt_text = f"""You are an AI that helps improve user ideas by asking specific, personalized questions.
My idea: {payload.idea}. Please ask 5-10 questions to clarify and improve this idea."""

    questions_text = query_deepseek_ollama(prompt_text)

    prompt_entry = Prompt(
        gmail_id=payload.gmail_id,
        idea=payload.idea,
        questions=questions_text,
        answers="",
        final_prompt=""
    )
    db.add(prompt_entry)
    db.commit()
    db.refresh(prompt_entry)

    return prompt_entry


# === Route: Refine Prompt from Answers ===
@router.post("/answer", response_model=PromptResponse)
def receive_answers(payload: PromptAnswerInput, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.gmail_id == payload.gmail_id).order_by(Prompt.timestamp.desc()).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt entry not found")

    user = db.query(User).filter(User.gmail_id == payload.gmail_id).first()
    if user.credits < 10:
        raise HTTPException(status_code=403, detail="Insufficient credits")
    user.credits -= 10
    db.commit()

    answers_text = "\n".join(payload.answers)

    refine_text = f"""You are an expert prompt engineer.
The user has this idea: {prompt.idea}
Here are their detailed responses: {answers_text}
Generate a clear, reusable AI prompt that can be given to an LLM to produce a high-quality, detailed output on this topic."""

    refined_prompt = query_deepseek_ollama(refine_text)

    prompt.answers = answers_text
    prompt.final_prompt = refined_prompt
    db.commit()
    db.refresh(prompt)

    return prompt


@router.get("/history/{gmail_id}", response_model=List[PromptResponse])
def get_user_chats(gmail_id: str, db: Session = Depends(get_db)):
    ist = timezone("Asia/Kolkata")
    prompts = db.query(Prompt).filter(Prompt.gmail_id == gmail_id).order_by(Prompt.timestamp.desc()).all()
    
    for prompt in prompts:
        prompt.timestamp = prompt.timestamp.astimezone(ist)
    
    return prompts


@router.get("/analytics/prompt-usage/{gmail_id}", response_model=PromptUsageStats)
def get_prompt_usage(gmail_id: str, db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=29)

    # 1. Total prompts count
    total_prompts = db.query(func.count()).filter(Prompt.gmail_id == gmail_id).scalar()

    # 2. Prompts grouped by day (last 30 days)
    prompts_per_day = (
        db.query(
            func.date(Prompt.timestamp).label("day"),
            func.count().label("count")
        )
        .filter(
            Prompt.gmail_id == gmail_id,
            Prompt.timestamp >= start_date
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    # 3. Most active day
    most_active_day = max(prompts_per_day, key=lambda x: x.count, default=None)

    return {
        "total_prompts": total_prompts,
        "daily_usage": [{"date": str(day), "count": count} for day, count in prompts_per_day],
        "most_active_day": str(most_active_day.day) if most_active_day else None
    }
