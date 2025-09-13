# utils/chat.py
from typing import List, Optional
from fastapi import HTTPException
from sqlmodel import Session, select

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.language_models import BaseLanguageModel

from config import settings
from models.user import User
from models.character import Character
from models.dialog import Dialog
from models.message import Message
from utils.for_ai import build_character_system_prompt


def ensure_character_access(session: Session, character_id: int, current_user: User) -> Character:
    """
    Проверяет существование персонажа и права доступа.
    Бросает HTTPException если доступ запрещён.
    """
    ch = session.get(Character, character_id)
    if not ch or ch.is_blocked:
        raise HTTPException(status_code=404, detail="Character not found")
    if not ch.is_public and ch.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Private character")
    return ch


def fetch_dialog_if_valid(
    session: Session,
    dialog_id: Optional[int],
    user_id: int,
    character_id: int,
) -> Optional[Dialog]:
    """
    Возвращает диалог, если dialog_id задан и пользователь/персонаж совпадают,
    иначе кидает 404. Если dialog_id не передан — возвращает None.
    """
    if not dialog_id:
        return None
    dialog = session.get(Dialog, dialog_id)
    if not dialog or dialog.user_id != user_id or dialog.character_id != character_id:
        raise HTTPException(status_code=404, detail="Dialog not found")
    return dialog


def create_dialog_with_context(
    session: Session,
    user_id: int,
    character_id: int,
    system_content: str,
) -> Dialog:
    """
    Создаёт диалог и первое системное сообщение (контекст персонажа).
    """
    dialog = Dialog(user_id=user_id, character_id=character_id)
    session.add(dialog)
    session.commit()
    session.refresh(dialog)

    sys_msg = Message(dialog_id=dialog.id, role="system", content=system_content)
    session.add(sys_msg)
    session.commit()

    return dialog


def add_message(session: Session, dialog_id: int, role: str, content: str) -> Message:
    """
    Создаёт и сохраняет сообщение.
    """
    msg = Message(dialog_id=dialog_id, role=role, content=content)
    session.add(msg)
    session.commit()
    session.refresh(msg)
    return msg


def fetch_history_messages(session: Session, dialog_id: int) -> List[Message]:
    """
    Возвращает всю историю сообщений в диалоге по возрастанию времени.
    """
    q = select(Message).where(Message.dialog_id == dialog_id).order_by(Message.created_at.asc())
    return session.exec(q).all()


def to_langchain_messages(history: List[Message]) -> List[BaseMessage]:
    """
    Конвертирует сообщения из БД в формат LangChain.
    """
    lc_messages: List[BaseMessage] = []
    for m in history:
        role = (m.role or "").lower()
        if role == "system":
            lc_messages.append(SystemMessage(content=m.content))
        elif role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        else:
            # "assistant"/"ai" и пр. попадают сюда
            lc_messages.append(AIMessage(content=m.content))
    return lc_messages


def get_llm(model_id: str = "lite", temperature: Optional[float] = None) -> BaseLanguageModel:
    """
    Возвращает LLM из settings с дефолтным model_id и температурой из настроек.
    """
    temp = settings.TEMPERATURE if temperature is None else temperature
    return settings.create_yandex_model(model_id=model_id, temperature=temp)


def generate_ai_response(
    llm: BaseLanguageModel,
    character: Character,
    lc_messages: List[BaseMessage],
) -> str:
    """
    Добавляет системный промпт персонажа и вызывает LLM.
    Возвращает чистый текст ответа.
    """
    char_sys = SystemMessage(content=build_character_system_prompt(character))
    ai_msg = llm.invoke([char_sys] + lc_messages + ['Ассистент: [SEP]'])
    return ai_msg.content if hasattr(ai_msg, "content") else str(ai_msg)