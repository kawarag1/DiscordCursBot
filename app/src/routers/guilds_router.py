from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.database import get_session
from app.src.schemas.response.guild_schema import GuildSchema
from app.src.schemas.response.member_schema import MemberSchema
from app.src.schemas.response.owner_schema import OwnerSchema
from app.src.schemas.request.ban_schema import BanSchema
from app.src.security.session_auth_token import session_auth
from app.src.security.oauth import get_current_owner
from app.src.services.guild_service import GuildService

router = APIRouter(prefix="/guilds", tags=["Сервера"])

@router.get("/guilds", dependencies=[Depends(session_auth)], description="Получение списка серверов владельца", response_model=list[GuildSchema])
async def get_guilds(owner: OwnerSchema = Depends(get_current_owner), session: AsyncSession = Depends(get_session)):
    return await GuildService(session).get_owned_guilds(owner=owner)

@router.get("/guilds/{guild_id}", dependencies=[Depends(session_auth)], description="Проверка наличия сервера в базе данных", response_model=bool)
async def check_guild(guild_id: str, session: AsyncSession = Depends(get_session)):
    return await GuildService(session).check_guild_by_id(int(guild_id))

@router.get("/guilds/{guild_id}/members", dependencies=[Depends(session_auth)], description="Получение списка участников сервера", response_model=list[MemberSchema])
async def get_guild_members(guild_id: str, owner: OwnerSchema = Depends(get_current_owner), session: AsyncSession = Depends(get_session)):
    return await GuildService(session).return_guild_members(int(guild_id))

@router.put("/guilds/{guild_id}/bans/{user_id}", dependencies=[Depends(session_auth)], description="Заблокировать участника на сервере")
async def ban_member(guild_id: str, user_id: str, ban_data: BanSchema, owner: OwnerSchema = Depends(get_current_owner), session: AsyncSession = Depends(get_session)):
    if ban_data.delete_user_messages:
        await GuildService(session).ban_member_with_message_deletion(owner.ds_id, int(guild_id), int(user_id), ban_data.reason)
    else:
        await GuildService(session).ban_member(owner.ds_id, int(guild_id), int(user_id), ban_data.reason)

@router.delete("/guilds/{guild_id}/members/{user_id}", dependencies=[Depends(session_auth)], description="Исключить участника с сервера")
async def kick_member(guild_id: str, user_id: str, ban_data: BanSchema, owner: OwnerSchema = Depends(get_current_owner), session: AsyncSession = Depends(get_session)):
    await GuildService(session).kick_member(owner.ds_id, int(guild_id), int(user_id), ban_data.reason)