from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.repo.user_repo import UserRepository
from app.src.schemas.request.user_schema import UserCreate


class UserService():
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def add_new_user(self, user: UserCreate):
        await self.user_repo.create(**user.model_dump())

    async def delete_user(self, ds_id: int):
        await self.user_repo.delete_messages_with_attachments(ds_id)
        id = await self.user_repo.get_userID_by_dsID(ds_id)
        await self.user_repo.delete_by_id(id)

    async def get_server_profile(self, ds_id: int):
        return await self.user_repo.get_by_ds_id(ds_id)

    async def change_server_profile(self, user: UserCreate):
        await self.user_repo.update_by_ds_id(user.ds_id, **user.model_dump())

    async def clear_users(self, guild_id: int):
        await self.user_repo.delete_users_by_guild_id(guild_id)

    async def get_userID_by_dsID(self, ds_id: int) -> int:
        return await self.user_repo.get_userID_by_dsID(ds_id)
        
