from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.src.routers.main_router import router



app = FastAPI(
    title="API для управления подписками на бота",
    description="Этот API позволяет управлять подписками на бота, включая создание, обновление и удаление подписок.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path="/api"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)