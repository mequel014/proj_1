# app/utils/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from utils.db import get_session
from utils.security import decode_token
from models.user import User

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