import datetime

import disnake
from disnake.ext import commands

from app.src.schemas.request.action_schema import BanSchema
from app.src.services.ban_service import BanService
from app.src.orm.database.database import async_session_factory

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="ban", description="Заблокировать пользователя")
    @commands.has_permissions(ban_members=True)
    async def ban(self, inter: disnake.ApplicationCommandInteraction,
                  user: disnake.Member,
                  reason: str = commands.Param(description="Причина блокировки", max_length=100),
                  days: int = commands.Param(description="Длительность блокировки в днях (0 для перманентного)", ge=0, le=7)):
        
        if user == inter.author:
            await inter.response.send_message(
                "❌ Вы не можете заблокировать самого себя!",
                ephemeral=True
            )
            return
        
        if user.guild_permissions.administrator:
            await inter.response.send_message(
                "❌ Вы не можете заблокировать администратора сервера!",
                ephemeral=True
            )
            return
        
        if user.top_role >= inter.author.top_role:
            await inter.response.send_message(
                "❌ Вы не можете заблокировать пользователя с ролью выше или равной вашей!",
                ephemeral=True
            )
            return
        
        try:
            duration_text = f"на {days} дней" if days > 0 else "навсегда"
            embed = disnake.Embed(
                title="Блокировка пользователя",
                description=f"**Пользователь:** {user.mention} ({user.id})\n"
                           f"**Причина:** {reason}\n"
                           f"**Длительность:** {duration_text}\n"
                           f"**Модератор:** {inter.author.mention}",
                color=disnake.Color.red(),
                timestamp=datetime.utcnow()
            )
            await inter.response.send(embed=embed)
        except:
            pass

        async with async_session_factory() as session:
            async with session.begin():
                ban_service = BanService(session)
                await ban_service.log_ban(
                    BanSchema(
                        guild_id=inter.guild.id,
                        user_id=inter.author.id,
                        action="ban",
                        reason=reason,
                        target_id=user.id,
                        details=f"Duration: {duration_text}",
                        created_at=datetime.datetime.utcnow()
                    )
                )

        await inter.guild.ban(user, reason=reason)
    
    @commands.slash_command(name="unban", description="Разбанить пользователя")
    @commands.has_permissions(ban_members=True)
    async def unban(self, inter: disnake.ApplicationCommandInteraction, user_id: str = commands.Param(description="ID пользователя для разблокировки")):
        try:
            user_id = int(user_id)
        except ValueError:
            await inter.response.send_message(
                "❌ Пожалуйста, введите действительный ID пользователя!",
                ephemeral=True
            )
            return
        
        ban_entries = await inter.guild.bans()

        target_user = None
        for ban_entry in ban_entries:
            if ban_entry.user.id == user_id:
                target_user = ban_entry.user
                break
        
        if not target_user:
            await inter.response.send_message(
                "❌ Этот пользователь не заблокирован!",
                ephemeral=True
            )
            return

        
        await inter.guild.unban(target_user)
        await inter.response.send_message(
            f"✅ Пользователь {target_user.mention} был разблокирован!",
            ephemeral=True)

        embed = disnake.Embed(
            title="✅ Бан снят",
            description=f"**Пользователь:** {target_user.mention}\n"
                       f"**ID:** {target_user.id}\n"
                       f"**Модератор:** {inter.author.mention}",
            color=disnake.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        await inter.response.send_message(embed=embed)

def setup(bot):
    pass