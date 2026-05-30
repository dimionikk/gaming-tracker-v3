from app.config import setting
from argon2 import PasswordHasher
from jose import jwt, JWTError
from fastapi.security import HTTPBearer
from fastapi import HTTPException, Depends
from datetime import datetime, timedelta
import secrets

pwd_context = PasswordHasher()
oauth2_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def veryfy_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(hashed_password, password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=setting.access_token_expire_minutes)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, setting.secret_key, setting.algorithm)

def create_refresh_token() -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    return token, expires_at

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, setting.secret_key, algorithms=[setting.algorithm])
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалідний токен")

def get_current_user(token: HTTPBearer = Depends(oauth2_scheme)) -> dict:
    return decode_access_token(token.credentials)