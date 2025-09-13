# app/routers/dialogs.py
# app/routers/dialogs.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from config import settings
from utils.db import get_session
from utils.dependencies import get_current_user
from models.user import User
from models.character import Character
from models.dialog import Dialog
from models.message import Message
from schemas.dialog import DialogOut, MessageOut, StartOrContinueChat, ChatResponse

from utils.chat import (
    ensure_character_access,
    fetch_dialog_if_valid,
    create_dialog_with_context,
    add_message,
    fetch_history_messages,
    to_langchain_messages,
    get_llm,
    generate_ai_response,
)

router = APIRouter()

@router.get("", response_model=List[DialogOut])
def my_dialogs(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    q = select(Dialog).where(Dialog.user_id == current_user.id).order_by(Dialog.started_at.desc())
    return session.exec(q).all()

@router.get("/{dialog_id}/messages", response_model=List[MessageOut])
def get_messages(dialog_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    dialog = session.get(Dialog, dialog_id)
    if not dialog or dialog.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Dialog not found")
    q = select(Message).where(Message.dialog_id == dialog_id).order_by(Message.created_at.asc())
    return session.exec(q).all()

@router.post("/{character_id}/messages", response_model=ChatResponse)
def send_message(
    character_id: int,
    data: StartOrContinueChat,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 1) Доступ к персонажу
    character = ensure_character_access(session, character_id, current_user)

    # 2) Получаем/создаём диалог
    dialog = fetch_dialog_if_valid(session, data.dialog_id, current_user.id, character.id)
    if dialog is None:
        dialog = create_dialog_with_context(
            session,
            user_id=current_user.id,
            character_id=character.id,
            system_content=character.context,
        )

    # 3) Сообщение пользователя
    add_message(session, dialog.id, "user", data.message)

    # 4) История -> LangChain
    history = fetch_history_messages(session, dialog.id)
    lc_messages = to_langchain_messages(history)

    # 5) Вызов LLM
    llm = get_llm(model_id="lite")
    text = generate_ai_response(llm, character, lc_messages)

    # 6) Ответ ассистента
    assistant = add_message(session, dialog.id, "assistant", text)

    return ChatResponse(
        dialog_id=dialog.id,
        assistant_message=assistant
    )