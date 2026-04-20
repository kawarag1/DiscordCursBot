from datetime import datetime

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
    async def ban(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.Member,
        reason: str = commands.Param(description="Причина блокировки", max_length=100),
        days: int = commands.Param(description="Длительность блокировки в днях (0 для перманентного)", ge=0, le=7)
    ):
        
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
                            details=f"Duration: {days} days",
                            created_at=datetime.utcnow()
                        )
                    )
        except Exception as e:
            print(f"❌ Ошибка при логировании бана: {e}")
        
        await inter.guild.ban(user, reason=f"{reason} | Забанен: {inter.author}")
        
        embed = disnake.Embed(
            title="✅ Пользователь заблокирован",
            description=f"**Пользователь:** {user.mention}\n"
                       f"**ID:** {user.id}\n"
                       f"**Причина:** {reason}\n"
                       f"**Длительность:** {days} дней\n"
                       f"**Модератор:** {inter.author.mention}",
            color=disnake.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        await inter.response.send_message(embed=embed)
    
    @commands.slash_command(name="unban", description="Разблокировать пользователя")
    @commands.has_permissions(ban_members=True)
    async def unban(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user_id: str = commands.Param(description="ID пользователя для разблокировки")
    ):
        
        try:
            user_id_int = int(user_id)
        except ValueError:
            await inter.response.send_message(
                "❌ Пожалуйста, введите действительный ID пользователя!",
                ephemeral=True
            )
            return
        
        ban_entries = await inter.guild.bans().flatten()
        
        target_user = None
        for ban_entry in ban_entries:
            if ban_entry.user.id == user_id_int:
                target_user = ban_entry.user
                break
        
        if not target_user:
            await inter.response.send_message(
                "❌ Этот пользователь не заблокирован!",
                ephemeral=True
            )
            return
        
        
        await inter.guild.unban(target_user, reason=f"Снят модератором: {inter.author}")
        
        try:
            async with async_session_factory() as session:
                async with session.begin():
                    ban_service = BanService(session)
                    await ban_service.log_ban(
                        BanSchema(
                            guild_id=inter.guild.id,
                            user_id=inter.author.id,
                            action="unban",
                            reason="Снятие блокировки",
                            target_id=user_id_int,
                            details=f"Снят модератором {inter.author}",
                            created_at=datetime.utcnow()
                        )
                    )
        except Exception as e:
            print(f"❌ Ошибка при логировании снятия блокировки: {e}")
        
        embed = disnake.Embed(
            title="✅ Блокировка снята",
            description=f"**Пользователь:** {target_user.mention}\n"
                       f"**ID:** {target_user.id}\n"
                       f"**Модератор:** {inter.author.mention}",
            color=disnake.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        await inter.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(AdminCog(bot))