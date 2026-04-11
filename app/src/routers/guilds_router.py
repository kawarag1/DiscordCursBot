from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.database import get_session
from app.src.schemas.response.guild_schema import GuildSchema
from app.src.schemas.response.owner_schema import OwnerSchema
from app.src.security.session_auth_token import session_auth
from app.src.security.oauth import get_current_owner
from app.src.services.guild_service import GuildService

router = APIRouter(prefix="/guilds", tags=["Сервера"])

@router.get("/guilds", dependencies=[Depends(session_auth)], description="Получение списка серверов владельца", response_model=list[GuildSchema])
async def get_guilds(owner: OwnerSchema = Depends(get_current_owner), session: AsyncSession = Depends(get_session)):
    return await GuildService(session).get_owned_guilds(owner=owner)