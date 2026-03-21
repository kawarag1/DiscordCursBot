from fastapi import APIRouter

from app.src.routers.command_router import router as command_router


router = APIRouter(
    prefix="/v1",
)

router.include_router(command_router)
