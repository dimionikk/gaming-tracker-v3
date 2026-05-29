from fastapi import FastAPI
from app.routers import games

app = FastAPI(title="Gaming Tracker v3 - steam-service")
app.include_router(games.router)
 