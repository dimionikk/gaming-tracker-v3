import httpx
from loguru import logger
from app.config import settings
import redis.asyncio as redis
import json
async def get_games_from_steam(steam_id: str) -> list:
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": settings.steam_api_key,
        "steamid": steam_id,
        "include_appinfo": True,
        "format": "json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        games = data.get("response", {}).get("games", [])
        logger.info(f"Got {len(games)} games for {steam_id}")
        return games
    
async def cache_games(steam_id: str, games: list) -> None:
    r = redis.from_url(settings.redis_url)
    await r.set(f"games:{steam_id}", json.dumps(games), ex=3600)
    logger.info(f"Cached games for {steam_id}")

async def get_cached_games(steam_id:str)->list:
    r=redis.from_url(settings.redis_url)
    data = await r.get(f"games:{steam_id}")
    if not data:
        return None
    logger.info(f"{steam_id}")
    return json.loads(data)