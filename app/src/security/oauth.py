from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.connector import get_session
from app.src.orm.database.repo.owner_repo import OwnerRepository
from app.src.schemas.response.owner_schema import OwnerSchema
from app.src.security.jwt_manager import JWTManager
from app.src.utils.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/me")


async def get_current_owner(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
):
    data = await JWTManager().decode_token(token)

    owner_id = data.get("sub")
    if not owner_id:
        logger.critical("Не найден sub (owner_id) в JWT токене!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера, попробуйте позже.",
        )
    owner = await OwnerRepository(session).get_by_id(owner_id)
    return OwnerSchema.model_validate(owner)