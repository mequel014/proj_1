# app/models/message.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, Literal
from enum import Enum

from sqlmodel import SQLModel, Field

# RoleType = Literal["system", "user", "assistant"]

class RoleEnum(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dialog_id: int = Field(index=True, foreign_key="dialog.id")
    role: RoleEnum = Field(index=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)