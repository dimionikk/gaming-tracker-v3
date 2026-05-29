from app.config import settings
from jose import jwt, JWTError
from fastapi.security import HTTPBearer
from fastapi import HTTPException
oauth2_scheme = HTTPBearer()

def decode_access_token(token:str)->dict:
    try:
        return jwt.decode(token,settings.secret_key,algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалідний токен")