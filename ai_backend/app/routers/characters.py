# app/routers/characters.py
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select

from utils.db import get_session
from utils.dependencies import get_current_user, require_admin
from models.user import User
from models.character import Character
from schemas.character import CharacterCreate, CharacterUpdate, CharacterOut

router = APIRouter()

@router.get("", response_model=List[CharacterOut])
def list_characters(
    session: Session = Depends(get_session),
    mine: bool = False,
    owner_id: Optional[int] = None,
    current_user: Optional[User] = Depends(get_current_user),
):
    q = select(Character).where(Character.is_blocked == False)
    if mine and current_user:
        q = q.where(Character.owner_id == current_user.id)
    elif owner_id:
        q = q.where(Character.owner_id == owner_id)
    else:
        q = q.where(Character.is_public == True)
    return session.exec(q.order_by(Character.created_at.desc())).all()

@router.post("", response_model=CharacterOut)
def create_character(
    data: CharacterCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ch = Character(
        owner_id=current_user.id,
        name=data.name,
        gender=data.gender,
        photo_url=data.photo_url,
        bio=data.bio,
        context=data.context,
        interests=data.interests or [],
        rating=data.rating or 0.0,
        is_public=data.is_public,
    )
    session.add(ch)
    session.commit()
    session.refresh(ch)
    return ch

@router.get("/{character_id}", response_model=CharacterOut)
def get_character(character_id: int, session: Session = Depends(get_session), current_user: Optional[User] = Depends(get_current_user)):
    ch = session.get(Character, character_id)
    if not ch or ch.is_blocked:
        raise HTTPException(status_code=404, detail="Character not found")
    if not ch.is_public:
        if not current_user or (current_user.id != ch.owner_id and not current_user.is_admin):
            raise HTTPException(status_code=403, detail="Private character")
    return ch

@router.patch("/{character_id}", response_model=CharacterOut)
def update_character(
    character_id: int,
    data: CharacterUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ch = session.get(Character, character_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Not found")
    if current_user.id != ch.owner_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ch, field, value)
    session.add(ch)
    session.commit()
    session.refresh(ch)
    return ch

@router.post("/{character_id}/block")
def block_character(character_id: int, session: Session = Depends(get_session), admin: User = Depends(require_admin)):
    ch = session.get(Character, character_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Not found")
    ch.is_blocked = not ch.is_blocked
    session.add(ch)
    session.commit()
    return {"detail": "toggled", "is_blocked": ch.is_blocked}

# Простой локальный аплоад картинки (опционально)
@router.post("/upload/photo")
def upload_photo(file: UploadFile = File(...)):
    os.makedirs("static/uploads", exist_ok=True)
    path = os.path.join("static", "uploads", file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return {"photo_url": f"/{path}"}