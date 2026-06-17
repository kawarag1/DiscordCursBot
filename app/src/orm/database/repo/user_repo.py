from sqlalchemy import delete, select

from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import Attachments, User, Messages
from app.src.schemas.request.user_update_schema import UserUpdate


class UserRepository(AbstractRepository):
    model = User

    async def get_userID_by_dsID(self, ds_id: int) -> int | None:
        query = select(self.model.id).where(self.model.ds_id == ds_id)
        result_ = await self._session.execute(query)
        result =  result_.scalars().first()

        if result is None:
            return None

        return result
    
    async def get_userDSID_by_user_ID(self, id: int) -> int | None:
        query = select(self.model.ds_id).where(self.model.id == id)
        result_ = await self._session.execute(query)
        result =  result_.scalars().first()

        if result is None:
            return None

        return result

    async def get_by_ds_id_guild(self, ds_id: int, guild_id: int) -> UserUpdate | None:
        query = select(self.model).where(self.model.ds_id == ds_id, self.model.guild_id == guild_id)
        result_ = await self._session.execute(query)
        result =  result_.scalars().first()
        if result:
            return UserUpdate(
                ds_id=result.ds_id,
                avatar_url=result.avatar_url if result.avatar_url else "",
                nickname=result.nickname,
                warnings=result.warnings
            )
        return None
    
    async def delete_users_by_guild_id(self, guild_id: int):
        await self._session.execute(delete(User).where(User.guild_id == guild_id))
 

    async def delete_messages_with_attachments(self, id: int):
        try:
            select_msg_id = select(Messages.id).where(Messages.user_id == id)
            msg_ids_result = await self._session.execute(select_msg_id)
            msg_ids = msg_ids_result.scalars().all()

            if not msg_ids:
                return 0
            
            delete_attachments = delete(Attachments).where(
                Attachments.message_id.in_(msg_ids)
            )
            await self._session.execute(delete_attachments)

            delete_messages = delete(Messages).where(Messages.user_id == id)
            result = await self._session.execute(delete_messages)

        except Exception as e:
            print(f"Ошибка при каскадном удалении: {e}")
    
    async def get_user_user_warnings(self, ds_id: int) -> int:
        query = select(self.model.warnings).where(self.model.ds_id == ds_id)
        result_ = await self._session.execute(query)
        result =  result_.scalars().first()

        if result is None:
            return 0

        return result
    
    async def add_warning(self, ds_id: int, guild_id: int) -> int:
        user = await self.get_by_ds_id_guild(ds_id, guild_id)
        if user:
            user.warnings = user.warnings + 1
            await self.update_by_ds_id(ds_id, warnings=user.warnings)
            return user.warnings

    async def clear_warnings(self, ds_id: int, guild_id: int):
        user = await self.get_by_ds_id_guild(ds_id, guild_id)
        if user:
            user.warnings = 0
            await self.update_by_ds_id(ds_id, warnings=user.warnings)

    async def check_user_exists(self, ds_id: int, guild_id: int) -> bool:
        query = select(self.model).where(self.model.ds_id == ds_id, self.model.guild_id == guild_id)
        result_ = await self._session.execute(query)
        result =  result_.scalars().first()
        return result is not None
        