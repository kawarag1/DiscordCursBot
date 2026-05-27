from pydantic_settings import BaseSettings
from yarl import URL
from functools import lru_cache

class Settings(BaseSettings):
    TOKEN: str
    CLIENT_ID: int
    CLIENT_SECRET: str
    REDIRECT_URI: str   
    AUTH_URI: str
    TOKEN_URI: str
    USER_URI: str
    GUILDS_URI: str
    GUILD_MEMBERS_URI: str
    KICK_URI: str
    BAN_URI: str

    YM_TOKEN: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    GMAIL_EMAIL: str
    GMAIL_PASSWORD: str    

    EMAIL_CONFIRM_CODE_TTL: int = 15

    REDIS_HOST: str | None = None
    REDIS_PORT: int | None = None
    REDIS_PASSWORD: str | None = None

    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_LIFETIME_MINUTES: int
    JWT_REFRESH_TOKEN_LIFETIME_DAYS: int
    JWT_SECRET_KEY: str

    JWT_REDIS_PREFIX: str = "jwt:"
    JWT_BLACKLIST_PREFIX: str = "blacklist:"
    JWT_USER_SESSIONS_PREFIX: str = "user_sessions:"
    COMMAND_REDIS_PREFIX: str = "blocked_command"

    class Config:
        env_file = ".env"

    @property
    def db_url(self) -> URL:
        url = URL.build (
            scheme="postgresql+asyncpg",
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            path=f"/{self.POSTGRES_DB}"
        )
        return url
    
    def redis_url(self, database: int = 0):
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{database}"
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{database}"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings: Settings = get_settings()