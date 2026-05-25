import disnake
from disnake.ext import commands
from datetime import datetime

from app.src.orm.database.database import async_session_factory
from app.src.services.message_service import MessageService

class MessageLogsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    async def create_embed(self, message: disnake.Message, moderator: disnake.Member = None):
        embed = disnake.Embed(
            title = "Сообщение отправлено",
            color=disnake.Color.green(),
            timestamp = datetime.now()
        )

        embed.add_field(
            name = "Содержание сообщения",
            value = message.content[:1024] if message.content else "Сообщение без текста",
            inline = False
        )

        embed.add_field(
            name = "Отправитель",
            value=f"{message.author.mention}\n`{message.author.name}#{message.author.discriminator}`",
            inline=True
        )

        embed.add_field(
            name="📁 Канал",
            value=f"{message.channel.mention}\n`{message.channel.name}`",
            inline=True
        )

        if moderator:
            embed.add_field(
                name="🛠️ Отправлено через",
                value=f"{moderator.mention}\n`{moderator.name}#{moderator.discriminator}`",
                inline=True
            )

        embed.add_field(
            name="🔗 Ссылка на сообщение",
            value=f"[Перейти]({message.jump_url})",
            inline=False
        )

        embed.set_footer(text=f"ID сообщения: {message.id} | Автор: {message.author.id}")

        embed.set_thumbnail(url=message.author.display_avatar.url)

        return embed

    

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return
        
        if message.channel.name in ["messages", "members"]:
            return  
        
        async with async_session_factory() as session:
            async with session.begin():
                message_service = MessageService(session)
                await message_service.add_message(message)
        guild = message.guild
        log_chanell_id = disnake.utils.get(guild.text_channels, name = "messages")
        if log_chanell_id:
            try:
                embed = await self.create_embed(message)
                await log_chanell_id.send(embed = embed)
            except Exception as e:
                print(f"Ошибка при логировании: {e}")

def setup(bot):
    bot.add_cog(MessageLogsCog(bot))
            
        
