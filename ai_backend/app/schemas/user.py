# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserPublic(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    display_name: Optional[str] = None
    created_at: datetime
    is_admin: bool = False
    is_blocked: bool = False

    class Config:
        from_attributes = True

class ShortDialog(BaseModel):
    id: int
    started_at: datetime
    character_name: str

class UserAdminDetail(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    characters: List[dict]
    short_dialogs: List[ShortDialog]

    class Config:
        from_attributes = True