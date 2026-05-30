from pydantic import BaseModel
from uuid import UUID

class SteamConnect(BaseModel):
    steam_id:str

class SteamConnectResponse(BaseModel):
    user_id:UUID
    steam_id:str

class Game(BaseModel):
    name:str
    playtime:int

class GameStats(BaseModel):
    total_games: int
    total_hours: float
    top_10: list[Game]