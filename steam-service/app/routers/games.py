from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import steam, models, schemas, auth
from app.database import get_async_session

router = APIRouter(prefix="/games", tags=["games"])

@router.post("/connect", response_model=schemas.SteamConnectResponse)
async def connect_steam(
    data: schemas.SteamConnect,
    session: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(auth.get_current_user)
):
    user_id = current_user["user_id"]
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
    current_user: dict = Depends(auth.get_current_user)
):
    user_id = current_user["user_id"]
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

@router.get("/stats", response_model=schemas.GameStats)
async def get_stats(
    session: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(auth.get_current_user)
):
    user_id = current_user["user_id"]
    result = await session.execute(select(models.User_steam).where(models.User_steam.user_id == user_id))
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        raise HTTPException(status_code=404)
    cached = await steam.get_cached_games(existing_user.steam_id)
    if cached:
        games = cached
    else:
        games = await steam.get_games_from_steam(existing_user.steam_id)
        await steam.cache_games(existing_user.steam_id, games)
    total_games = len(games)
    total_hours = round(sum(g["playtime"] for g in games) / 60, 1)
    top_10 = sorted(games, key=lambda g: g["playtime"], reverse=True)[:10]
    return {"total_games": total_games, "total_hours": total_hours, "top_10": top_10}