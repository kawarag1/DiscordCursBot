from datetime import datetime
import disnake
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.models.models import Messages as ModelMessage, Attachments as ModelAttachment
from app.src.orm.database.repo.user_repo import UserRepository

class MessageService():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_message(self, message: disnake.Message):
        ds_id = await UserRepository.get_userID_by_dsID(message.author.id)

        message_ = ModelMessage(
            id = message.id,
            user_id = message.ds_id,
            guild_id = message.guild.id,
            content = message.content,
            created_at = message.created_at
        )
        self.session.add(message_)

        for attachment_ in range(len(message.attachments)):
            attachment = message.attachments[attachment_]
            new_attachment = ModelAttachment(
                id = attachment.id,
                message_id = message.id,
                url = attachment.url,
                content_type = attachment.content_type
            )
            self.session.add(new_attachment)
        await self.session.commit()