import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.repo.log_repo import LogRepository
from app.src.schemas.request.action_schema import ActionSchema
from app.src.schemas.response.action_schema import MemberActionSchema, ActionSchema as ResponceActionSchema
from app.src.schemas.response.raw_action_schema import RawActionSchema
from app.src.settings import settings


class ActionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_action(self, action: ActionSchema):
        await LogRepository(self.session).create(**action.model_dump())

    async def get_raw_actions(self, guild_id: int) -> list[RawActionSchema]:
        return await LogRepository(self.session).get_by_guild_id(guild_id)

    async def get_user_by_id(self, user_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://discord.com/api/users/{user_id}",
                headers={"Authorization": f"Bot {settings.BOT_TOKEN}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
    
    async def get_actions(self, guild_id: int) -> list[ResponceActionSchema]:
        raw_actions = await self.get_raw_actions(guild_id)
        actions: list[ResponceActionSchema] = []
        for action in raw_actions:
            user_data = await self.get_user_by_id(action.user_id)
            target_data = await self.get_user_by_id(action.target_id)

            actions.append(ResponceActionSchema(
                id=action.id,
                user_id=MemberActionSchema(
                    username=user_data.get("username") if user_data else "Unknown User",
                    avatar_url=(
                        f"https://cdn.discordapp.com/avatars/{user_data.get('id')}/{user_data.get('avatar')}.png"
                        if user_data and user_data.get("avatar")
                        else None
                    )
                ),
                target_id=MemberActionSchema(
                    username=target_data.get("username") if target_data else "Unknown User",
                    avatar_url=(
                        f"https://cdn.discordapp.com/avatars/{target_data.get('id')}/{target_data.get('avatar')}.png"
                        if target_data and target_data.get("avatar")
                        else None
                    )
                ),
                guild_id=action.guild_id,
                action=action.action,
                reason=action.reason,
                details=action.details,
                created_at=action.created_at
            ))
        return actions
    

    
