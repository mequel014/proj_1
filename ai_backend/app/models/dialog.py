# app/models/dialog.py
from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

class Dialog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    character_id: int = Field(index=True, foreign_key="character.id")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None