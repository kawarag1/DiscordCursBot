
from fastapi import Depends
from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.schemas.request.disable_command_schema import DisableCommandSchema
from app.src.orm.database.repo.command_repo import CommandRepository
from app.src.orm.models.models import DisabledCommands as ModelCommand
from app.src.utils.redis.redis_client import AsyncRedisClient, get_redis
from app.src.settings.settings import settings

class CommandService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def disable_command(self, command: DisableCommandSchema):
        result = await CommandRepository(self.session).create(guild_id=int(command.guild_id), command_name=command.command_name)
        result.guild_id = str(result.guild_id)
        return result
    
    async def enable_command(self, command: DisableCommandSchema):
        query = select(ModelCommand).filter(
            ModelCommand.guild_id == int(command.guild_id),
            ModelCommand.command_name == command.command_name
        )


        delete_query = delete(ModelCommand).filter(
            ModelCommand.guild_id == int(command.guild_id),
            ModelCommand.command_name == command.command_name
        )

        result_ = await self.session.execute(query)
        await self.session.execute(delete_query)
        await self.session.commit()
        result = result_.scalars().first()
        result.guild_id = str(result.guild_id)
        return result
    
    async def check_command(self, command: DisableCommandSchema):
        query = select(exists().where(
            ModelCommand.guild_id == int(command.guild_id),
            ModelCommand.command_name == command.command_name
        ))
        result = await self.session.execute(query)
        
        return not result.scalar()
    