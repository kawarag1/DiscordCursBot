from datetime import datetime

import disnake
from disnake.ext import commands

from app.src.schemas.request.action_schema import ActionSchema
from app.src.services.action_service import ActionService
from app.src.orm.database.database import async_session_factory
from app.src.services.user_service import UserService


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="ban", description="Заблокировать пользователя")
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.Member,
        reason: str = commands.Param(description="Причина блокировки", max_length=100)
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
        
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message(
                "❌ Вы не обладете правами администратора!",
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
                    action_service = ActionService(session)
                    user_service = UserService(session)
                    user_id = await user_service.get_userID_by_DS_ID(inter.author.id)
                    target_user_id = await user_service.get_userID_by_DS_ID(user.id)
                    await action_service.log_action(
                        ActionSchema(
                            guild_id=inter.guild.id,
                            user_id=user_id,
                            action="ban",
                            reason=reason,
                            target_id=target_user_id,
                            details=f"Ban from ds",
                            created_at=datetime.utcnow()
                        )
                    )
        except Exception as e:
            print(f"❌ Ошибка при логировании бана: {e}")
        
        await inter.guild.ban(user, reason=f"{reason} | Заблокирован: {inter.user.mention}")
        
        await inter.response.defer(ephemeral=True)
        
        await inter.edit_original_response(content=f"✅ Пользователь {inter.user.mention} заблокирован.")
    
    @commands.slash_command(name="unban", description="Разблокировать пользователя")
    @commands.has_permissions(ban_members=True)
    async def unban(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user_id: str = commands.Param(description="ID пользователя для разблокировки")
    ):
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message(
                "❌ Вы не обладете правами администратора!",
                ephemeral=True
            )
            return
        
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
                    action_service = ActionService(session)
                    user_service = UserService(session)
                    _user_id = await user_service.get_userID_by_DS_ID(inter.author.id)
                    target_user_id = await user_service.get_userID_by_DS_ID(user_id_int)
                    await action_service.log_action(
                        ActionSchema(
                            guild_id=inter.guild.id,
                            user_id=_user_id,
                            action="unban",
                            reason="Снятие блокировки",
                            target_id=target_user_id,
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
        
        channel = disnake.utils.get(inter.guild.text_channels, name = "members")
        if channel:
            channel.send(embed=embed)
        
        await inter.response.defer(ephemeral=True)
        
        await inter.edit_original_response(content=f"✅ Пользователь {inter.user.mention} исключён.")

    @commands.slash_command(name="kick", description="Исключить пользователя")
    @commands.has_permissions(kick_members=True)
    async def kick(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.Member,
        reason: str = commands.Param(description="Причина исключения", max_length=100)
    ):
        
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message(
                "❌ Вы не обладете правами администратора!",
                ephemeral=True
            )
            return
        
        if user == inter.author:
            await inter.response.send_message(
                "❌ Вы не можете исключить самого себя!",
                ephemeral=True
            )
            return
        
        if user.guild_permissions.administrator:
            await inter.response.send_message(
                "❌ Вы не можете исключить администратора сервера!",
                ephemeral=True
            )
            return
        
        if user.top_role >= inter.author.top_role:
            await inter.response.send_message(
                "❌ Вы не можете исключить пользователя с ролью выше или равной вашей!",
                ephemeral=True
            )
            return

        
        try:
            async with async_session_factory() as session:
                async with session.begin():
                    action_service = ActionService(session)
                    user_service = UserService(session)
                    user_id = await user_service.get_userID_by_DS_ID(inter.author.id)
                    target_user_id = await user_service.get_userID_by_DS_ID(user.id)
                    await action_service.log_action(
                        ActionSchema(
                            guild_id=inter.guild.id,
                            user_id=user_id,
                            action="kick",
                            reason=reason,
                            target_id=target_user_id,
                            details="",
                            created_at=datetime.utcnow()
                        )
                    )
        except Exception as e:
            print(f"❌ Ошибка при логировании исключения: {e}")
        
        await inter.guild.kick(user, reason=f"{reason} | Исключен: {inter.author}")
        
        embed = disnake.Embed(
            title="✅ Пользователь исключен",
            description=f"**Пользователь:** {user.mention}\n"
                       f"**ID:** {user.id}\n"
                       f"**Причина:** {reason}\n"
                       f"**Модератор:** {inter.author.mention}",
            color=disnake.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        await inter.response.send_message(embed=embed)



def setup(bot):
    bot.add_cog(AdminCog(bot))