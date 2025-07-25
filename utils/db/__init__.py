from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

from utils.config import config

DATABASE_URL = config.db_connect_uri

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False 
)

async def getSession():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
            
async def init_db():
    from utils.db.schemas import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 