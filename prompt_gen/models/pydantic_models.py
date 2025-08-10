from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    gmail_id: str
    user_name: str
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    gmail_id: str
    user_name: str
    credits: int = 100

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    gmail_id: str
    password: str

class SuccessLogin(BaseModel):
    user_name: str
    gmail_id: str
    access_token: str  
    

class PromptCreate(BaseModel):
    gmail_id: str
    idea: str

class PromptAnswerInput(BaseModel):
    gmail_id: str
    answers: list[str]

class PromptResponse(BaseModel):
    id: int
    idea: str
    questions: str
    answers: str
    final_prompt: str
    timestamp: datetime

    class Config:
        from_attributes = True



class GoogleAuthRequest(BaseModel):
    token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class DailyPromptCount(BaseModel):
    date: str
    count: int

class PromptUsageStats(BaseModel):
    total_prompts: int
    daily_usage: List[DailyPromptCount]
    most_active_day: Optional[str]