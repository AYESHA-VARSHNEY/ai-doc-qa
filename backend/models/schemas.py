from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    file_id: str
    question: str

class ChatResponse(BaseModel):
    answer: str
    timestamp: Optional[float] = None
    source: Optional[str] = None

class SummaryRequest(BaseModel):
    file_id: str

class SummaryResponse(BaseModel):
    summary: str
    file_name: str
    file_type: str
