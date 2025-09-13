# app/schemas/character.py
from pydantic import BaseModel
from typing import List, Optional

class CharacterCreate(BaseModel):
    name: str
    gender: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    context: str
    interests: List[str] = []
    rating: Optional[float] = 0.0
    is_public: bool = True

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    context: Optional[str] = None
    interests: Optional[List[str]] = None
    rating: Optional[float] = None
    is_public: Optional[bool] = None

class CharacterOut(BaseModel):
    id: int
    owner_id: int
    name: str
    gender: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    context: str
    interests: List[str]
    rating: Optional[float]
    is_public: bool
    is_blocked: bool

    class Config:
        from_attributes = True