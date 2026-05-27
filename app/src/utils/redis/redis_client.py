from functools import lru_cache
from typing import AsyncGenerator

import redis.asyncio as redis

from app.src.schemas.response.access_token import AccessToken
from app.src.settings.settings import settings
from app.src.utils.logger.logger import logger


class AsyncRedisClient:
    def __init__(self, database: int = 0):
        self._redis = None
        self.database = database
        self.url = settings.redis_url(database)
        logger.info(f"redis url: {self.url}")

    async def connect(self):
        self._redis = await redis.from_url(self.url, decode_responses=True)

    async def close(self):
        if self._redis:
            await self._redis.close()

    async def check_user_tokens(self, user_id, token: str, expires_in: int):
        stored_token = await self._redis.get(f"{settings.JWT_REDIS_PREFIX}access:{str(user_id)}")
        if stored_token:
            await self.revoke_all_user_tokens(user_id)

            await self.store_access_token(user_id, token, expires_in)
        else:
            await self.store_access_token(user_id, token, expires_in)


    async def get_user_tokens(self, user_id: int) -> AccessToken | None:
        access_token = await self._redis.get(f"{settings.JWT_REDIS_PREFIX}access:{str(user_id)}")
        refresh_token = await self._redis.get(f"{settings.JWT_REDIS_PREFIX}refresh:{str(user_id)}")

        if access_token and refresh_token:
            return AccessToken(access_token=access_token, refresh_token=refresh_token)
        return None

    async def revoke_all_user_tokens(self, user_id: int):
        access_token = await self._redis.get(f"{settings.JWT_REDIS_PREFIX}access:{str(user_id)}")
        refresh_token = await self._redis.get(f"{settings.JWT_REDIS_PREFIX}refresh:{str(user_id)}")

        if access_token:
            await self._redis.delete(f"{settings.JWT_REDIS_PREFIX}access:{str(user_id)}")
        if refresh_token:
            await self._redis.delete(f"{settings.JWT_REDIS_PREFIX}refresh:{str(user_id)}")

    async def store_access_token(self, user_id: int, token: str, expires_in: int):
        key = f"{settings.JWT_REDIS_PREFIX}access:{str(user_id)}"
        await self._redis.setex(key, expires_in, token)
        
    async def store_refresh_token(self, user_id: int, token: str, expires_in: int):
        key = f"{settings.JWT_REDIS_PREFIX}refresh:{str(user_id)}"
        await self._redis.setex(key, expires_in, token)

def get_redis(db_num: int = 0):
    async def _get_redis() -> AsyncGenerator[AsyncRedisClient, None]:
        redis_client = AsyncRedisClient(db_num)
        try:
            await redis_client.connect()
            yield redis_client
        finally:
            await redis_client.close()
        
    return _get_redis


@lru_cache
def get_redis_client() -> AsyncRedisClient:
    return AsyncRedisClient()