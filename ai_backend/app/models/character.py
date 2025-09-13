# app/models/character.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field

class Character(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    owner_id: int = Field(index=True, foreign_key="user.id")

    name: str
    gender: Optional[str] = None
    photo_url: Optional[str] = None

    bio: Optional[str] = None
    context: str  # системное сообщение при старте диалога

    interests: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    rating: Optional[float] = 0.0

    is_public: bool = True
    is_blocked: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)