from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
async_session_maker=async_sessionmaker(engine,expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_async_session():
    async with async_session_maker() as session:
        yield session