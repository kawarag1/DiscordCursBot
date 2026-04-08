from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.database import get_session
from app.src.schemas.response.owner_schema import OwnerSchema
from app.src.orm.database.repo.owner_repo import OwnerRepository
from app.src.security.session_auth_token import session_auth

async def get_current_owner(session_token: str = Depends(session_auth), session: AsyncSession = Depends(get_session)) -> OwnerSchema:
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    
    owner = await OwnerRepository(session).get_by_session_token(session_token)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    return owner