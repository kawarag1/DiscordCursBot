import disnake
from datetime import datetime
from typing import Optional

class MemberLogs:
    @staticmethod
    async def create_join_embed(member: disnake.Member):
        
        embed = disnake.Embed(
            title="✅ Присоединился к серверу",
            color=disnake.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.description = f"**{member.name}** присоединился к серверу"
        
        embed.add_field(
            name="👤 Пользователь",
            value=f"{member.mention}\n`{member.name}#{member.discriminator}`",
            inline=True
        )
        
        embed.add_field(
            name="🆔 ID",
            value=f"```{member.id}```",
            inline=True
        )
        
        embed.add_field(
            name="📅 Аккаунт создан",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=False
        )
        
        embed.add_field(
            name="👥 Участников на сервере",
            value=f"`{member.guild.member_count}`",
            inline=True
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID пользователя: {member.id}")
        
        return embed
    
    @staticmethod
    async def create_leave_embed(member: disnake.Member, roles: Optional[list] = None):
        
        embed = disnake.Embed(
            title="❌ Покинул сервер",
            color=disnake.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.description = f"**{member.name}** покинул сервер"
        
        embed.add_field(
            name="👤 Пользователь",
            value=f"`{member.name}#{member.discriminator}`",
            inline=True
        )
        
        embed.add_field(
            name="🆔 ID",
            value=f"```{member.id}```",
            inline=True
        )
        
        if member.joined_at:
            embed.add_field(
                name="📅 Присоединился",
                value=f"<t:{int(member.joined_at.timestamp())}:R>\n"
                      f"На сервере: <t:{int(member.joined_at.timestamp())}:D>",
                inline=False
            )
        
        if roles and len(roles) > 0:
            roles_text = ", ".join([role.mention for role in roles[:5]])
            if len(roles) > 5:
                roles_text += f" и еще {len(roles) - 5}..."
            embed.add_field(
                name=f"🎭 Роли ({len(roles)})",
                value=roles_text if roles_text else "Нет ролей",
                inline=False
            )
        
        embed.add_field(
            name="👥 Осталось участников",
            value=f"`{member.guild.member_count}`",
            inline=True
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID пользователя: {member.id}")
        
        return embed