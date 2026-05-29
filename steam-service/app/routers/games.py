from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import steam, models, schemas
from app.database import get_async_session
from app.auth import decode_access_token, oauth2_scheme

router = APIRouter(prefix="/games", tags=["games"])

@router.post("/connect", response_model=schemas.SteamConnectResponse)
async def connect_steam(
    data: schemas.SteamConnect,
    session: AsyncSession = Depends(get_async_session),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    result = await session.execute(select(models.User_steam).where(models.User_steam.user_id == user_id))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=409)
    user_steam = models.User_steam(user_id=user_id, steam_id=data.steam_id)
    session.add(user_steam)
    await session.commit()
    return user_steam

@router.get("/games", response_model=list[schemas.Game])
async def get_games(
    session: AsyncSession = Depends(get_async_session),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    result = await session.execute(select(models.User_steam).where(models.User_steam.user_id == user_id))
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        raise HTTPException(status_code=404)
    cached = await steam.get_cached_games(existing_user.steam_id)
    if cached:
        return cached
    games = await steam.get_games_from_steam(existing_user.steam_id)
    await steam.cache_games(existing_user.steam_id, games)
    return games