from typing import Optional
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import *
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    ds_id: Mapped[BIGINT] = mapped_column(BigInteger, autoincrement = False)
    nickname: Mapped[str] = mapped_column(String(256))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone = True), default = datetime)
    message_count: Mapped[BIGINT] = mapped_column(BigInteger, default = 0)
    level: Mapped[int] = mapped_column(Integer, default = 1)
    warnings: Mapped[int] = mapped_column(Integer, default = 0)
    guild_id: Mapped[BIGINT] = mapped_column(BigInteger, ForeignKey("Guilds.id"))

    guilds: Mapped["Guild"] = relationship("Guild", back_populates = "users")
    messages: Mapped["Messages"] = relationship("Messages", back_populates = "users")
    logs: Mapped["Log_entries"] = relationship("Log_entries", back_populates = "users")
    

class Owner(Base):
    __tablename__ = "Owners"
    id: Mapped[BIGINT] = mapped_column(BigInteger, primary_key = True, autoincrement = True)
    ds_id: Mapped[BIGINT] = mapped_column(BigInteger, unique = True)
    email: Mapped[Optional[str]] = mapped_column(String(256), unique = True)

    guilds: Mapped["Guild"] = relationship("Guild", back_populates = "owners")

class Guild(Base):
    __tablename__ = "Guilds"
    id: Mapped[BIGINT] = mapped_column(BigInteger, primary_key = True)
    name: Mapped[str] = mapped_column(String(256))
    owner_id: Mapped[Optional[BIGINT]] = mapped_column(BigInteger, ForeignKey("Owners.ds_id"))
    icon_hash: Mapped[Optional[str]] = mapped_column(String(256))
    welcome_message: Mapped[Optional[str]] = mapped_column(Text, nullable = True)

    owners: Mapped["Owner"] = relationship("Owner", back_populates = "guilds")
    users: Mapped["User"] = relationship("User", back_populates = "guilds")
    messages: Mapped["Messages"] = relationship("Messages", back_populates = "guilds")
    logs: Mapped["Log_entries"] = relationship("Log_entries", back_populates = "guilds")
    disabled_commands: Mapped["DisabledCommands"] = relationship("DisabledCommands", back_populates = "guilds")

class DisabledCommands(Base):
    __tablename__ = "DisabledCommands"
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    guild_id: Mapped[BIGINT] = mapped_column(BigInteger, ForeignKey("Guilds.id"))
    command_name: Mapped[str] = mapped_column(String(256))

    guilds: Mapped["Guild"] = relationship("Guild", back_populates = "disabled_commands")

class Messages(Base):
    __tablename__ = "Messages"
    id: Mapped[BIGINT] = mapped_column(BigInteger, primary_key = True, autoincrement = True)
    user_id: Mapped[BIGINT] = mapped_column(BigInteger, ForeignKey("Users.id"))
    guild_id: Mapped[BIGINT] = mapped_column(BigInteger, ForeignKey("Guilds.id"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone = True), default = datetime)

    users: Mapped["User"] = relationship("User", back_populates = "messages")
    guilds: Mapped["Guild"] = relationship("Guild", back_populates = "messages")
    attachments: Mapped["Attachments"] = relationship("Attachments", back_populates = "messages")

class Attachments(Base):
    __tablename__ = "Attachments"
    id: Mapped[BIGINT] = mapped_column(BigInteger, primary_key = True, autoincrement = True)
    message_id: Mapped[BIGINT] = mapped_column(BigInteger, ForeignKey("Messages.id"))
    url: Mapped[str] = mapped_column(String(512))
    content_type: Mapped[str] = mapped_column(String(128))

    messages: Mapped["Messages"] = relationship("Messages", back_populates = "attachments")


class Log_entries(Base):
    __tablename__ = "Log_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    user_id: Mapped[BIGINT] = mapped_column(BigInteger, ForeignKey("Users.id"))
    guild_id: Mapped[BIGINT] = mapped_column(BigInteger, ForeignKey("Guilds.id"))
    action: Mapped[str] = mapped_column(String)
    target_id: Mapped[BIGINT] = mapped_column(BigInteger)
    reason: Mapped[str] = mapped_column(Text)
    details: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone = True), default = datetime)

    users: Mapped["User"] = relationship("User", back_populates = "logs")
    guilds: Mapped["Guild"] = relationship("Guild", back_populates = "logs")
