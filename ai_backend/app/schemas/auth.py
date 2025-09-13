# app/schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class RequestSignup(BaseModel):
    email: EmailStr

class CompleteSignup(BaseModel):
    token: str
    password: str
    username: Optional[str] = None
    display_name: Optional[str] = None

class LoginRequest(BaseModel):
    login: str  # email или username
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"