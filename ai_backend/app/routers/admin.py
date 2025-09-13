# app/routers/admin.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from utils.db import get_session
from utils.dependencies import require_admin
from models.user import User
from models.character import Character
from models.dialog import Dialog
from models.message import Message
from schemas.admin import Stats
from schemas.user import UserPublic, UserAdminDetail, ShortDialog
from schemas.dialog import MessageOut

router = APIRouter()

@router.get("/stats", response_model=Stats)
def stats(_: User = Depends(require_admin), session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    characters = session.exec(select(Character)).all()
    dialogs = session.exec(select(Dialog)).all()
    messages = session.exec(select(Message)).all()
    return Stats(
        users=len(users),
        characters=len(characters),
        dialogs=len(dialogs),
        messages=len(messages),
    )

@router.get("/users", response_model=List[UserPublic])
def list_users(_: User = Depends(require_admin), session: Session = Depends(get_session)):
    q = select(User).order_by(User.created_at.desc())
    return session.exec(q).all()

@router.get("/users/{user_id}", response_model=UserAdminDetail)
def user_detail(user_id: int, _: User = Depends(require_admin), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")

    chars = session.exec(select(Character).where(Character.owner_id == user.id)).all()
    dialogs = session.exec(select(Dialog).where(Dialog.user_id == user.id).order_by(Dialog.started_at.desc())).all()

    short_dialogs: List[ShortDialog] = []
    for d in dialogs:
        ch = session.get(Character, d.character_id)
        short_dialogs.append(ShortDialog(id=d.id, started_at=d.started_at, character_name=ch.name if ch else "Unknown"))

    return UserAdminDetail(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        characters=[{'id': c.id, 'name': c.name} for c in chars],
        short_dialogs=short_dialogs,
    )

@router.get("/dialogs/{dialog_id}", response_model=List[MessageOut])
def admin_dialog_detail(dialog_id: int, _: User = Depends(require_admin), session: Session = Depends(get_session)):
    q = select(Message).where(Message.dialog_id == dialog_id).order_by(Message.created_at.asc())
    return session.exec(q).all()

@router.post("/users/{user_id}/block")
def toggle_user_block(user_id: int, admin: User = Depends(require_admin), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    user.is_blocked = not user.is_blocked
    session.add(user)
    session.commit()
    return {"detail": "toggled", "is_blocked": user.is_blocked}