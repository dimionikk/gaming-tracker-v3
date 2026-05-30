from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app import models, schemas, auth
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=schemas.UserResponse)
async def register(data: schemas.UserCreate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(models.User).where(models.User.email == data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=409)
    hashed_password = auth.hash_password(data.password)
    user = models.User(username=data.username, email=data.email, password=hashed_password)
    session.add(user)
    await session.commit()
    return user

@router.post("/login", response_model=schemas.TokenPair)
async def login(data: schemas.UserLogin, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(models.User).where(models.User.email == data.email))
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        raise HTTPException(status_code=404)
    if not auth.veryfy_password(data.password, existing_user.password):
        raise HTTPException(status_code=401)
    access_token = auth.create_access_token({"sub": existing_user.email, "user_id": str(existing_user.id)})
    refresh_token, expires_at = auth.create_refresh_token()
    db_token = models.RefreshToken(user_id=existing_user.id, token=refresh_token, expires_at=expires_at)
    session.add(db_token)
    await session.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=schemas.TokenPair)
async def refresh(data: schemas.RefreshTokenRequest, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(models.RefreshToken).where(models.RefreshToken.token == data.refresh_token))
    db_token = result.scalar_one_or_none()
    if not db_token:
        raise HTTPException(status_code=401, detail="Невалідний refresh токен")
    if db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh токен протух")
    await session.delete(db_token)
    user_result = await session.execute(select(models.User).where(models.User.id == db_token.user_id))
    user = user_result.scalar_one_or_none()
    access_token = auth.create_access_token({"sub": user.email, "user_id": str(user.id)})
    new_refresh_token, expires_at = auth.create_refresh_token()
    new_db_token = models.RefreshToken(user_id=user.id, token=new_refresh_token, expires_at=expires_at)
    session.add(new_db_token)
    await session.commit()
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
async def get_me(current_user: dict = Depends(auth.get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(models.User).where(models.User.id == UUID(current_user["user_id"])))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404)
    return user

@router.delete("/me", status_code=204)
async def delete_me(current_user: dict = Depends(auth.get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(models.User).where(models.User.id == UUID(current_user["user_id"])))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404)
    await session.delete(user)
    await session.commit()

@router.patch("/me", response_model=schemas.UserResponse)
async def update_me(data: schemas.UserUpdate, current_user: dict = Depends(auth.get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(models.User).where(models.User.id == UUID(current_user["user_id"])))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404)
    if data.username:
        user.username = data.username
    if data.email:
        user.email = data.email
    if data.password:
        user.password = auth.hash_password(data.password)
    await session.commit()
    return user