from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)

from alembic.config import Config
from alembic import command

from ..models.models import Base
from app.src.settings.settings import settings

async def get_engine() -> AsyncEngine:
    return create_async_engine(str(settings.db_url))

engine = create_async_engine(str(settings.db_url))
async_session_factory = async_sessionmaker(bind = engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    async_session = sessionmaker(await get_engine(), class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    try:
        engine = await get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Migration successful")
    except Exception as e:
        print("Не удалось создать таблицы. ", str(e))

def run_migrations():
    alembic_cfg = Config("alembic.ini")

    database_url = settings.db_url
    if database_url:
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    command.upgrade(alembic_cfg, "head")
