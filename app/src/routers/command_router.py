from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.database import get_session
from app.src.schemas.request.disable_command_schema import DisableCommandSchema
from app.src.services.command_service import CommandService

router = APIRouter(prefix="/commands", tags=["Отключение команд бота"])


@router.post("/disable", description="Отключить команду бота", response_model=DisableCommandSchema)
async def disable_command(command: DisableCommandSchema, session: AsyncSession = Depends(get_session)):
    return await CommandService(session).disable_command(command)

@router.delete("/enable", description="Включить команду бота", response_model=DisableCommandSchema)
async def enable_command(command: DisableCommandSchema, session: AsyncSession = Depends(get_session)):
    return await CommandService(session).enable_command(command)