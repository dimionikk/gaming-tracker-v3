from fastapi import FastAPI
from app.routers import users
app = FastAPI(title="Gaming Tracker v3 - user-service")

app.include_router(users.router)

