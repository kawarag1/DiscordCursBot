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
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone = True), default = datetime)
    message_count: Mapped[BIGINT] = mapped_column(BigInteger, default = 0)
    level: Mapped[int] = mapped_column(Integer, default = 1)
    guild_id: Mapped[BIGINT] = mapped_column(BigInteger, ForeignKey("Guilds.id"))

    guilds: Mapped["Guild"] = relationship("Guild", back_populates = "users")
    messages: Mapped["Messages"] = relationship("Messages", back_populates = "users")
    logs: Mapped["Log_entries"] = relationship("Log_entries", back_populates = "users")

class Guild(Base):
    __tablename__ = "Guilds"
    id: Mapped[BIGINT] = mapped_column(BigInteger, primary_key = True)
    name: Mapped[str] = mapped_column(String(256))
    config_json: Mapped[Optional[str]] = mapped_column(Text)

    users: Mapped["User"] = relationship("User", back_populates = "guilds")
    messages: Mapped["Messages"] = relationship("Messages", back_populates = "guilds")
    logs: Mapped["Log_entries"] = relationship("Log_entries", back_populates = "guilds")

class Messages(Base):
    __tablename__ = "Messages"
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.ds_id"))
    guild_id: Mapped[BIGINT] = mapped_column(BigInteger, ForeignKey("Guilds.id"))
    content: Mapped[str] = mapped_column(Text)
    has_images: Mapped[bool] = mapped_column(Boolean)
    image_url: Mapped[Optional[str]] = mapped_column(String(512))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone = True), default = datetime)

    users: Mapped["User"] = relationship("User", back_populates = "messages")
    guilds: Mapped["Guild"] = relationship("Guild", back_populates = "messages")


class Log_entries(Base):
    __tablename__ = "Log_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.ds_id"))
    guild_id: Mapped[BIGINT] = mapped_column(BigInteger, ForeignKey("Guilds.id"))
    action: Mapped[str] = mapped_column(String) #ban, mute, kick, role_add, voice_leave, member_join, member_leave
    target_id: Mapped[Optional[str]] = mapped_column(String)
    reason: Mapped[str] = mapped_column(Text)
    details: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone = True), default = datetime)

    users: Mapped["User"] = relationship("User", back_populates = "logs")
    guilds: Mapped["Guild"] = relationship("Guild", back_populates = "logs")
