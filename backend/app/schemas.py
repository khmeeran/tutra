from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uuid
from datetime import date

class Token(BaseModel):
    access_token: str
    token_type: str

class ParentRegister(BaseModel):
    email: EmailStr
    phone: str
    password: str
    name: str

class LoginRequest(BaseModel):
    identifier: str
    password: str

class StudentCreate(BaseModel):
    name: str
    medium: str
    school_name: str
    board_id: uuid.UUID
    grade_id: uuid.UUID
    academic_year: str

class ChatRequest(BaseModel):
    subject_id: uuid.UUID
    message: str

class ChatResponse(BaseModel):
    response: str
