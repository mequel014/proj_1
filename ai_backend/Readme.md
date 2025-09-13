# LLM Chat — FastAPI + SQLModel + YandexGPT (LangChain)

Ниже — минималистичный, но расширяемый бэкенд-проект на FastAPI. Он покрывает:
- регистрацию по email-ссылке и вход по JWT,
- профили пользователей,
- персонажи (карточки с фото, полом, именем, интересами, рейтингом, контекстом),
- диалоги (хранение истории, первое системное сообщение — контекст персонажа),
- админку (просмотр пользователей/диалогов, блокировка пользователей/персонажей),
- интеграцию с YandexGPT через langchain_openai.

Проект специально сделан простым, без «тяжёлых» решений, чтобы было удобно дальше масштабировать.

Запуск: через fastapi dev (без uvicorn / gunicorn).  
База: SQLite локально (sqlmodel).

---

## Быстрый старт

1) Установите зависимости (минимальный набор):
```
python -m venv .venv
# Linux/Mac:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -U "fastapi[standard]" sqlmodel python-dotenv langchain-openai python-multipart
```

2) Создайте .env в корне проекта (рядом с папкой app/) по примеру ниже.

3) Запустите сервер:
```
fastapi dev app/main.py
```

4) Откройте Swagger: http://127.0.0.1:8000/docs

---

## Структура проекта

```
.
├─ .env                         # ваши секреты и настройки (пример ниже)
├─ app/
│  ├─ main.py                   # точка входа FastAPI
│  ├─ config.py                 # настройки (Yandex LLM, БД, JWT), адаптировано под ваш config.py
│  ├─ models/                   # модели БД (SQLModel)
│  │  ├─ __init__.py
│  │  ├─ user.py
│  │  ├─ character.py
│  │  ├─ dialog.py
│  │  └─ message.py
│  ├─ schemas/                  # pydantic-схемы запросов/ответов
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  ├─ user.py
│  │  ├─ character.py
│  │  ├─ dialog.py
│  │  └─ admin.py
│  ├─ routers/                  # роутеры (эндпоинты)
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  ├─ characters.py
│  │  ├─ dialogs.py
│  │  └─ admin.py
│  └─ utils/                    # утилиты: БД, безопасность, "почта" и зависимости
│     ├─ __init__.py
│     ├─ db.py
│     ├─ security.py
│     ├─ email.py
│     └─ dependencies.py
└─ static/
   └─ uploads/                  # сюда можно класть загруженные картинки
```

---

## .env пример

Скопируйте и подставьте свои значения (особенно API_KEY и FOLDER_ID):

```
# Yandex LLM
API_KEY=ваш_yandex_api_key
FOLDER_ID=ваш_folder_id
BASE_URL=https://llm.api.cloud.yandex.net/foundationModels/v1
TEMPERATURE=0.2

# LangSmith (необязательно)
LANGSMITH_API=
LANGSMITH_PROJECT=

# Database
DATABASE_URL=sqlite:///./app.db
DB_ECHO=false

# JWT
JWT_SECRET=change-me-to-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## Что делает каждый файл и код

### app/main.py
- Создаёт приложение FastAPI
- Инициализирует БД
- Подключает роутеры
- Монтирует статику
- Включает CORS

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.utils.db import create_db_and_tables
from app.routers import auth, characters, dialogs, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="LLM Chat Backend", lifespan=lifespan)

# Простой CORS (под фронт локально)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # на проде сузьте!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статика (для картинок персонажей, если захотите)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(characters.router, prefix="/characters", tags=["characters"])
app.include_router(dialogs.router, prefix="/dialogs", tags=["dialogs"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Для проверки
@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}
```

---

### app/config.py
- Ваш config.py + незначительные дополнения под JWT и удобство.
- Создаёт LLM-клиент YandexGPT через langchain_openai.

```python
# app/config.py
import os
from dotenv import load_dotenv
from functools import lru_cache
from typing import Optional

from langchain_openai import ChatOpenAI

load_dotenv()

class Settings:
    # Yandex LLM
    API_KEY: str = os.getenv("API_KEY", "")
    FOLDER_ID: str = os.getenv("FOLDER_ID", "")
    BASE_URL: str = os.getenv("BASE_URL", "https://llm.api.cloud.yandex.net/foundationModels/v1")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))

    # LangSmith (опционально)
    LANGSMITH_API: str = os.getenv("LANGSMITH_API", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Маппинг имён моделей
    MODEL_NAMES = {
        'lite': 'yandexgpt-lite',
        'pro': 'yandexgpt',
        'pro_32k': 'yandexgpt-32k',
    }

    def model_name(self, model_id: str) -> str:
        """
        gpt://<folder>/<model>/latest — формат для Yandex Cloud
        """
        return f"gpt://{self.FOLDER_ID}/{self.MODEL_NAMES[model_id]}/latest"

    @lru_cache()
    def create_yandex_model(self, model_id: str = "lite", temperature: Optional[float] = None) -> ChatOpenAI:
        """
        Создаёт (и кеширует) клиент YandexGPT через langchain_openai
        """
        if temperature is None:
            temperature = self.TEMPERATURE

        llm = ChatOpenAI(
            api_key=self.API_KEY,
            base_url=self.BASE_URL,
            model=self.model_name(model_id),
            temperature=temperature,
        )
        return llm


settings = Settings()

# Настройка переменных для LangSmith (если нужно)
if settings.LANGSMITH_API:
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API
if settings.LANGSMITH_PROJECT:
    os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT
```

---

### app/models/ — модели БД (SQLModel)

Примечания:
- SQLite, никаких миграций — просто создаём таблицы при старте.
- interests у персонажа — JSON-массив (list[str]), чтобы не делать отдельные таблицы для тегов (просто и достаточно для MVP).
- Храним сообщения чата: role ∈ {"system", "user", "assistant"}.

#### app/models/user.py
```python
# app/models/user.py
from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    email: str = Field(index=True)
    username: Optional[str] = Field(default=None, index=True)
    display_name: Optional[str] = None

    hashed_password: Optional[str] = Field(default=None, nullable=True)
    email_verified: bool = False

    is_active: bool = True
    is_admin: bool = False
    is_blocked: bool = False

    verification_token: Optional[str] = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### app/models/character.py
```python
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
```

#### app/models/dialog.py
```python
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
```

#### app/models/message.py
```python
# app/models/message.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, Literal

from sqlmodel import SQLModel, Field

RoleType = Literal["system", "user", "assistant"]

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dialog_id: int = Field(index=True, foreign_key="dialog.id")
    role: RoleType
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### app/schemas/ — pydantic-схемы

#### app/schemas/auth.py
```python
# app/schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class RequestSignup(BaseModel):
    email: EmailStr

class CompleteSignup(BaseModel):
    token: str
    password: str
    username: Optional[str] = None
    display_name: Optional[str] = None

class LoginRequest(BaseModel):
    login: str  # email или username
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

#### app/schemas/user.py
```python
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
    characters: List[str]
    short_dialogs: List[ShortDialog]

    class Config:
        from_attributes = True
```

#### app/schemas/character.py
```python
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
```

#### app/schemas/dialog.py
```python
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
```

#### app/schemas/admin.py
```python
# app/schemas/admin.py
from pydantic import BaseModel

class Stats(BaseModel):
    users: int
    characters: int
    dialogs: int
    messages: int
```

---

### app/utils/ — утилиты

#### app/utils/db.py
- Инициализация движка, сессии и создание таблиц

```python
# app/utils/db.py
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DB_ECHO, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

#### app/utils/security.py
- Минимальная реализация JWT на стандартной библиотеке (HS256)
- Хеширование пароля через PBKDF2-HMAC (без внешних зависимостей)

```python
# app/utils/security.py
import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from app.config import settings

# --- Password hashing (PBKDF2-HMAC-SHA256) ---
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${dk.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, hex_hash = hashed.split("$", 1)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
        return hmac.compare_digest(dk.hex(), hex_hash)
    except Exception:
        return False

# --- Minimal JWT (HS256) ---
def _b64url_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

def _b64url_decode(s: str) -> bytes:
    padding = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)

def create_access_token(subject: str, expires_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES, extra: Optional[Dict[str, Any]] = None) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {"sub": subject, "iat": now, "exp": now + expires_minutes * 60}
    if extra:
        payload.update(extra)

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(settings.JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def decode_token(token: str) -> Dict[str, Any]:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")

    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = _b64url_decode(sig_b64)
    expected = hmac.new(settings.JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature")

    payload = json.loads(_b64url_decode(payload_b64))
    exp = payload.get("exp")
    if not exp or int(time.time()) > int(exp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    return payload
```

#### app/utils/email.py
- Для MVP “отправка письма” — просто лог ссылки в консоль

```python
# app/utils/email.py
def send_signup_link(email: str, link: str):
    # В реальном проекте отправляйте письмо через SMTP / сервисы
    print(f"[SIGNUP LINK] Send to {email}: {link}")
```

#### app/utils/dependencies.py
- Зависимости для получения текущего пользователя и проверки админа

```python
# app/utils/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.utils.db import get_session
from app.utils.security import decode_token
from app.models.user import User

security = HTTPBearer(auto_error=True)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    user_id = int(payload.get("sub", 0))
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active or user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive or blocked")
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user
```

---

### app/routers/ — роутеры (эндпоинты)

#### app/routers/auth.py
- Регистрация по email-ссылке (генерируем token и “шлём” ссылку в консоль)
- Завершение регистрации (по token выставляем пароль, и т.д.)
- Логин (email или username) -> JWT
- /me — информация о текущем пользователе

```python
# app/routers/auth.py
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select

from app.schemas.auth import RequestSignup, CompleteSignup, LoginRequest, TokenResponse
from app.schemas.user import UserPublic
from app.models.user import User
from app.utils.db import get_session
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.dependencies import get_current_user
from app.utils.email import send_signup_link

router = APIRouter()

@router.post("/request-signup")
def request_signup(data: RequestSignup, request: Request, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if user and user.hashed_password:
        # уже зарегистрирован — отвечаем 200, чтобы не палить наличие email
        return {"detail": "If email exists, a link has been sent."}

    if not user:
        user = User(email=data.email)
        session.add(user)
        session.commit()
        session.refresh(user)

    token = secrets.token_urlsafe(32)
    user.verification_token = token
    session.add(user)
    session.commit()

    # В консоль — ссылку (в реальности отправляйте письмо)
    base = str(request.base_url).rstrip("/")
    link = f"{base}/auth/complete-signup?token={token}"
    send_signup_link(user.email, link)

    return {"detail": "If email exists, a link has been sent."}

@router.post("/complete-signup")
def complete_signup(data: CompleteSignup, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.verification_token == data.token)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    if data.username:
        # Проверим уникальность username по-простому
        exists = session.exec(select(User).where(User.username == data.username)).first()
        if exists and exists.id != user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    user.hashed_password = hash_password(data.password)
    user.email_verified = True
    user.verification_token = None
    user.username = data.username or user.username
    if data.display_name is not None:
        user.display_name = data.display_name

    session.add(user)
    session.commit()
    session.refresh(user)
    return {"detail": "Signup completed"}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    # логин может быть email или username
    q = select(User).where((User.email == data.login) | (User.username == data.login))
    user = session.exec(q).first()
    if not user or not user.hashed_password or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active or user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive or blocked")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)):
    return current_user
```

#### app/routers/characters.py
- Публичный список персонажей (или только мои)
- Создание/редактирование персонажа
- Простая загрузка картинки (опционально)

```python
# app/routers/characters.py
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select

from app.utils.db import get_session
from app.utils.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterOut

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
```

#### app/routers/dialogs.py
- Список моих диалогов
- Получение сообщений диалога
- Отправка сообщения: создаёт новый диалог при необходимости, записывает системный контекст, обращается к YandexGPT (через langchain_openai), сохраняет ответ

```python
# app/routers/dialogs.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.config import settings
from app.utils.db import get_session
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.models.character import Character
from app.models.dialog import Dialog
from app.models.message import Message
from app.schemas.dialog import DialogOut, MessageOut, StartOrContinueChat, ChatResponse

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

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
    ch = session.get(Character, character_id)
    if not ch or ch.is_blocked:
        raise HTTPException(status_code=404, detail="Character not found")
    if not ch.is_public and ch.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Private character")

    dialog: Optional[Dialog] = None

    if data.dialog_id:
        dialog = session.get(Dialog, data.dialog_id)
        if not dialog or dialog.user_id != current_user.id or dialog.character_id != ch.id:
            raise HTTPException(status_code=404, detail="Dialog not found")
    else:
        dialog = Dialog(user_id=current_user.id, character_id=ch.id)
        session.add(dialog)
        session.commit()
        session.refresh(dialog)
        # Первое системное сообщение — контекст персонажа
        sys_msg = Message(dialog_id=dialog.id, role="system", content=ch.context)
        session.add(sys_msg)
        session.commit()

    # Записываем сообщение пользователя
    user_msg = Message(dialog_id=dialog.id, role="user", content=data.message)
    session.add(user_msg)
    session.commit()
    session.refresh(user_msg)

    # Готовим историю для LLM
    q = select(Message).where(Message.dialog_id == dialog.id).order_by(Message.created_at.asc())
    history = session.exec(q).all()

    lc_messages = []
    for m in history:
        if m.role == "system":
            lc_messages.append(SystemMessage(content=m.content))
        elif m.role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        else:
            lc_messages.append(AIMessage(content=m.content))

    # Вызов YandexGPT через LangChain
    llm = settings.create_yandex_model(model_id="lite", temperature=settings.TEMPERATURE)
    ai_msg = llm.invoke(lc_messages)
    text = ai_msg.content if hasattr(ai_msg, "content") else str(ai_msg)

    # Сохраняем ответ ассистента
    assistant = Message(dialog_id=dialog.id, role="assistant", content=text)
    session.add(assistant)
    session.commit()
    session.refresh(assistant)

    return ChatResponse(
        dialog_id=dialog.id,
        assistant_message=assistant
    )
```

#### app/routers/admin.py
- Статистика
- Список пользователей (минимально)
- Детали пользователя (дата регистрации, список персонажей, короткий список диалогов: дата, имя персонажа)
- Детальный диалог в виде чата
- Блокировка пользователя и персонажей

```python
# app/routers/admin.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.utils.db import get_session
from app.utils.dependencies import require_admin
from app.models.user import User
from app.models.character import Character
from app.models.dialog import Dialog
from app.models.message import Message
from app.schemas.admin import Stats
from app.schemas.user import UserPublic, UserAdminDetail, ShortDialog
from app.schemas.dialog import MessageOut

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
        characters=[c.name for c in chars],
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
```

---

## Потоки фронта (как это использовать)

- Регистрация по email:
  1) POST /auth/request-signup с email — в лог сервера упадёт ссылка.
  2) По ссылке (или фронт получает token из письма) вызвать POST /auth/complete-signup c token, password, username (optional).
  3) Затем POST /auth/login с login (email или username) и password — получите access_token.

- Персонажи:
  - GET /characters — список публичных.
  - GET /characters?mine=true — только мои (нужен токен).
  - POST /characters — создать персонажа (нужен токен).
  - PATCH /characters/{id} — редактировать (владелец или админ).
  - POST /characters/upload/photo — простой аплоад локально (вернёт photo_url).

- Диалоги:
  - POST /dialogs/{character_id}/messages — отправить сообщение.
    - Если dialog_id в теле не указан — создастся новый диалог (системное сообщение = контекст).
    - Вернёт ответ ассистента и dialog_id (для продолжения).
  - GET /dialogs — список ваших диалогов.
  - GET /dialogs/{dialog_id}/messages — получить историю.

- Админка:
  - GET /admin/stats — базовая статистика.
  - GET /admin/users — список пользователей.
  - GET /admin/users/{user_id} — детали пользователя (дата регистрации, созданные персонажи, «короткие» диалоги).
  - GET /admin/dialogs/{dialog_id} — сообщения диалога.
  - POST /characters/{id}/block — блокировка персонажа (админ).
  - POST /admin/users/{id}/block — блокировка пользователя.

Чтобы сделать кого-то админом, вручную поставьте is_admin=1 у пользователя (например, временно через SQLite-браузер или отдельным скриптом).

---

## Заметки и рекомендации

- JWT реализован вручную (HS256, exp). Для продакшена можно заменить на PyJWT/python-jose, но текущей минимальной реализации достаточно для MVP.
- Хеширование пароля — PBKDF2-HMAC-SHA256 из стандартной библиотеки, 100k итераций.
- interests у персонажа — JSON-массив (List[str]) в БД. Этого достаточно для тегов на фронте.
- Упрощённая «отправка письма» — просто лог ссылки. Подключите SMTP/почтовый сервис позже.
- YandexGPT: используем langchain_openai.ChatOpenAI, модель задаётся форматом gpt://<folder>/<model>/latest. Проверьте, что API-ключ и FOLDER_ID корректны.
- Проект максимально простой — без миграций, без сложных зависимостей. Можно спокойно рефакторить по мере роста.

---

## Примеры запросов (curl)

- Регистрация:
```
curl -X POST http://127.0.0.1:8000/auth/request-signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
# Скопируйте token из лога и:
curl -X POST http://127.0.0.1:8000/auth/complete-signup \
  -H "Content-Type: application/json" \
  -d '{"token":"<TOKEN_FROM_LOG>","password":"pass123","username":"user1"}'
```

- Логин:
```
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"user@example.com","password":"pass123"}'
# получите access_token
```

- Создать персонажа:
```
curl -X POST http://127.0.0.1:8000/characters \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "name":"Alice",
        "gender":"female",
        "photo_url":"/static/uploads/alice.png",
        "bio":"Легкая ирония, любит шахматы",
        "context":"Ты — Алиса, сидишь в уютной кофейне и думаешь о следующей книге...",
        "interests":["chess","books","coffee"],
        "rating":9.1,
        "is_public": true
      }'
```

- Начать диалог:
```
curl -X POST http://127.0.0.1:8000/dialogs/1/messages \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"message":"Привет! О чем думаешь?"}'
```

- Продолжить диалог:
```
curl -X POST http://127.0.0.1:8000/dialogs/1/messages \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"message":"А давай сыграем в шахматы?", "dialog_id": 5}'
```

---

Готово. Этот каркас можно легко расширять: добавлять роли, более умную модерацию, историю диалогов, аналитику, платежи и т.д. Если захочешь — помогу оптимизировать подсказки для LLM и добавить стриминг ответов.