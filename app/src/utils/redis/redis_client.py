from functools import lru_cache
from typing import AsyncGenerator

import redis.asyncio as redis

from app.src.schemas.request.disable_command_schema import DisableCommandSchema
from app.src.settings.settings import settings
from app.src.utils.logger import logger


class AsyncRedisClient:
    def __init__(self, database: int = 0):
        self._redis = None
        self.database = database
        self.url = settings.redis_url(database)
        logger.info(f"redis url: {self.url}")

    async def connect(self):
        """Установить соединение."""
        self._redis = await redis.from_url(self.url, decode_responses=True)

    async def close(self):
        """Закрыть соединение."""
        if self._redis:
            await self._redis.close()

    async def set_value(self, key, value, ttl=None):
        """Асинхронно сохранить значение."""
        if ttl:
            return await self._redis.setex(key, ttl, value)
        return await self._redis.set(key, value)

    async def get_value(self, key):
        """Асинхронно получить значение."""
        return await self._redis.get(key)
    
    async def delete_value(self, key):
        await self._redis.delete(key)
    

    async def check_user_tokens(self, user_id, token: str, expires_in: int):
        session_key = f"{settings.JWT_USER_SESSIONS_PREFIX}{user_id}"
        tokens = await self._redis.smembers(session_key)
        if tokens:
            await self.revoke_all_user_tokens(user_id)

            await self.store_access_token(user_id, token, expires_in)
        else:
            await self.store_access_token(user_id, token, expires_in)

    async def store_access_token(self, user_id: int, token: str, expires_in: int):
        key = f"{settings.JWT_REDIS_PREFIX}access:{token}"
        await self._redis.setex(key, expires_in, str(user_id))
                
        session_key = f"{settings.JWT_USER_SESSIONS_PREFIX}{user_id}"
            
        await self._redis.sadd(session_key, token)
        await self._redis.expire(session_key, expires_in * 2)
        
        
    async def store_refresh_token(self, user_id: int, token: str, expires_in: int):
        key = f"{settings.JWT_REDIS_PREFIX}refresh:{token}"
        await self._redis.setex(key, expires_in, str(user_id))

        session_key = f"{settings.JWT_USER_SESSIONS_PREFIX}{user_id}"

        await self._redis.sadd(session_key, token)
        await self._redis.expire(session_key, expires_in * 2)

    async def revoke_all_user_tokens(self, user_id: int):
        session_key = f"{settings.JWT_USER_SESSIONS_PREFIX}{user_id}"
        tokens = await self._redis.smembers(session_key)
        
        for token in tokens:
            if isinstance(token, bytes):
                token = token.decode('utf-8')

            access_key = f"{settings.JWT_REDIS_PREFIX}access:{token}"
            refresh_key = f"{settings.JWT_REDIS_PREFIX}refresh:{token}"

            access_ttl = await self._redis.ttl(access_key)
            refresh_ttl = await self._redis.ttl(refresh_key)


            if access_ttl > 0:
                await self.blacklist_token(token, access_ttl)
            
            if refresh_ttl > 0:
                await self.blacklist_token(token, refresh_ttl)
            
            await self._redis.delete(access_key, refresh_key)
        
        await self._redis.delete(session_key)

    async def blacklist_token(self, token: str, expires_in: int):
        key = f"{settings.JWT_BLACKLIST_PREFIX}{token}"
        await self._redis.setex(key, expires_in, "blacklisted")
    
    async def is_token_blacklisted(self, token: str) -> bool:
        key = f"{settings.JWT_BLACKLIST_PREFIX}{token}"
        return await self._redis.exists(key) > 0

    async def add_disabled_command(self, command: DisableCommandSchema):
        key = f"{settings.COMMAND_REDIS_PREFIX}{command.guild_id}"
        await self._redis.setex(key, 600, command.command_name)

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