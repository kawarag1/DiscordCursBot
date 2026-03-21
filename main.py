from fastapi import FastAPI

from app.src.routers.main_router import router



app = FastAPI(
    title="API для управления подписками на бота",
    description="Этот API позволяет управлять подписками на бота, включая создание, обновление и удаление подписок.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(router)