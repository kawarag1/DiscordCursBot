from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
import subprocess
import sys

from alembic.config import Config
from alembic import command

from app.src.utils.logger import logger
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


async def migrate():
    print("Checking for database migrations...")
    logger.info("Checking for database migrations...")

    try:
        # Запускаем alembic upgrade
        result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Migration failed: {result.stderr}")
        else:
            logger.info("Database migrations applied successfully")
            print("Database migrations applied successfully")
    except Exception as e:
        print(f"Migration error: {e}")
        logger.error(f"Migration error: {str(e)}")

def run_migrations():
    alembic_cfg = Config("alembic.ini")

    database_url = settings.db_url
    if database_url:
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    command.upgrade(alembic_cfg, "head")
