# app/utils/security.py
import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from config import settings

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