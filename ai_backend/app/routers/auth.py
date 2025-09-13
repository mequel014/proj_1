# app/routers/auth.py
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select

from schemas.auth import RequestSignup, CompleteSignup, LoginRequest, TokenResponse
from schemas.user import UserPublic
from models.user import User
from utils.db import get_session
from utils.security import hash_password, verify_password, create_access_token
from utils.dependencies import get_current_user
from utils.email import send_signup_link

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
    # base = str(request.base_url).rstrip("/")
    base = 'http://localhost:3000'
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