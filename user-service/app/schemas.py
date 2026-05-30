from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль має бути мінімум 8 символів")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator("password")
    def password_min_length(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError("Пароль має бути мінімум 8 символів")
        return v