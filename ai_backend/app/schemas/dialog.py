# app/schemas/dialog.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Literal

class StartOrContinueChat(BaseModel):
    message: str
    dialog_id: Optional[int] = None  # если пусто — создадим новый диалог

class MessageOut(BaseModel):
    id: int
    role: Literal["system", "user", "assistant"]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class DialogOut(BaseModel):
    id: int
    user_id: int
    character_id: int
    started_at: datetime

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    dialog_id: int
    assistant_message: MessageOut