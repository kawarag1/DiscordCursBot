from sqlalchemy import select, exists, update
from datetime import datetime

from app.src.orm.database.repo.abc_repo import AbstractRepository
from app.src.orm.models.models import Owner
from app.src.schemas.response.owner_schema import OwnerSchema

class OwnerRepository(AbstractRepository):
    model = Owner

    async def get_by_ds_id(self, ds_id: int):
        query = select(self.model).where(self.model.ds_id == ds_id)
        result_ = await self._session.execute(query)
        result = result_.scalars().first()
        if result:
            return OwnerSchema(
                id=result.id,
                ds_id=result.ds_id,
                email=result.email if result.email else "",
                refresh_token=result.refresh_token
            )
        return None

    async def exists_by_ds_id(self, ds_id: int) -> bool:
        query = select(exists(select(self.model).where(self.model.ds_id == ds_id)))
        result = await self._session.execute(query)
        return result.scalar()

    async def update_refresh_token(self, ds_id: int, access_token: str, refresh_token: str, session_token: str, expires_at: int | datetime):
        query = update(self.model).where(self.model.ds_id == ds_id).values(
            access_token=access_token,
            refresh_token=refresh_token,
            session_token=session_token,
            expires_at=expires_at
        )
        await self._session.execute(query)
        await self.commit()