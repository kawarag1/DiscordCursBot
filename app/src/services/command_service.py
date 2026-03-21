
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.schemas.request.disable_command_schema import DisableCommandSchema
from app.src.orm.database.repo.command_repo import CommandRepository
from app.src.orm.models.models import DisabledCommands as ModelCommand

class CommandService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def disable_command(self, command: DisableCommandSchema):
        await CommandRepository.create(**command.model_dump())

    async def enable_command(self, command: DisableCommandSchema):
        query = select(ModelCommand).filter(
            ModelCommand.guild_id == command.guild_id,
            ModelCommand.command_name == command.command_name
        )


        delete_query = delete(ModelCommand).filter(
            ModelCommand.guild_id == command.guild_id,
            ModelCommand.command_name == command.command_name
        )

        result = await self.session.execute(query)
        await self.session.execute(delete_query)
        self.session.commit()
        return result.scalars().first()
    