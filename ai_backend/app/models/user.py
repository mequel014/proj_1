# app/models/user.py
from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    email: str = Field(index=True)
    username: Optional[str] = Field(default=None, index=True)
    display_name: Optional[str] = None

    hashed_password: Optional[str] = Field(default=None, nullable=True)
    email_verified: bool = False

    is_active: bool = True
    is_admin: bool = False
    is_blocked: bool = False

    verification_token: Optional[str] = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)