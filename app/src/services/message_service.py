from datetime import datetime
import disnake
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.orm.models.models import Messages as ModelMessage, Attachments as ModelAttachment

class MessageService():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_message(self, message: disnake.Message):
        message_ = ModelMessage(
            id = message.id,
            user_id = message.author.id,
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