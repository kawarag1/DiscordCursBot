from typing import Optional
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import *
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    ds_id: Mapped[BIGINT] = mapped_column(BigInteger, primary_key = True, autoincrement = False)
    nickname: Mapped[str] = mapped_column(String(256))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512))
    tag: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone = True), default = datetime)


class ServerProfile(Base):
    __tablename__ = "ServerProfiles"
    id: Mapped[BIGINT] = mapped_column(BigInteger, primary_key = True)
    ds_id: Mapped[BIGINT] = mapped_column(BigInteger, ForeignKey("Users.ds_id"))
    server_nickname: Mapped[str] = mapped_column(String(256))
    message_count: Mapped[BIGINT] = mapped_column(BigInteger, default = 0)
    level: Mapped[int] = mapped_column(Integer, default = 1)

