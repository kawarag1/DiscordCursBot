from sqlalchemy import select, exists

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
            )
        return None

    async def exists_by_ds_id(self, ds_id: int) -> bool:
        query = select(exists(select(self.model).where(self.model.ds_id == ds_id)))
        result = await self._session.execute(query)
        return result.scalar()    