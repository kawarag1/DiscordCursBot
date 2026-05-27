from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.database import get_session
from app.src.schemas.response.action_schema import ActionSchema
from app.src.security.oauth import get_current_owner
from app.src.services.action_service import ActionService


router = APIRouter(prefix="/actions", tags=["Действия на серверах"])

@router.get("/{guild_id}", description="Получение списка действий на сервере", response_model=list[ActionSchema])
async def get_actions(guild_id: str, owner = Depends(get_current_owner), session: AsyncSession = Depends(get_session)):
    return await ActionService(session).get_actions(int(guild_id))