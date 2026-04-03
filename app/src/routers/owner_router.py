from fastapi import APIRouter, Depends, Response
from fastapi.params import Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.database.database import get_session
from app.src.schemas.request.code import CodeRequest
from app.src.schemas.response.owner_schema import OwnerSchema
from app.src.services.owner_service import OwnerService

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/get_owner", description="Авторизация владельца", response_model=OwnerSchema)
async def exchange_code(code: CodeRequest, response: Response, session: AsyncSession = Depends(get_session)):
    owner_token = await OwnerService(session).exchange_code(code=code.code)
    ds_id = await OwnerService(session).get_owner_info(owner_token.access_token)
    response.set_cookie(
        key="session_token",
        value=owner_token.session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=owner_token.expires_in)
    return await OwnerService(session).add_owner(ds_id, owner_token.access_token, owner_token.refresh_token, owner_token.session_token, owner_token.expires_at)
