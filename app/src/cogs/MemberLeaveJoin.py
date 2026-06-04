import disnake
from disnake.ext import commands
from datetime import datetime

from app.src.services.guild_service import GuildService
from app.src.services.user_service import UserService
from app.src.orm.database.database import async_session_factory
from app.src.schemas.request.user_schema import UserCreate

class MemberLeaveJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def format_welcome_message(self, template: str, user: disnake.Member, guild: disnake.Guild) -> str:
        replacements = {
            "{user}": user.mention,
            "{server}": guild.name,
            "{member_count}": str(guild.member_count),
            "{owner}": guild.owner.mention if guild.owner else "Неизвестно",
        }
        
        result = template
        for key, value in replacements.items():
            result = result.replace(key, value)
        
        return result

    async def create_welcome_embed(self, member: disnake.Member, message: str | None) -> disnake.Embed:
        embed = disnake.Embed(
            title = "Добро пожаловать!",
            description = message if message else f"мы приветствуем тебя, {member.mention}, ты пришёл на **{member.guild.name}**",
            color = disnake.Color.red(),
            timestamp = datetime.now())
        
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="👥 Участников",
            value=f"Теперь нас: **{len(member.guild.members)}**",
            inline=True)
        
        embed.add_field(
                name="📅 Дата регистрации",
                value=f"<t:{int(member.created_at.timestamp())}:D>",
                inline=True)
        
        embed.set_footer(text="Приятного общения!")
        
        return embed
    

    async def create_remove_embed(self, member: disnake.Member):
        embed = disnake.Embed(
                title = "Плохие новости",
                description = f"{member.mention}, решил уйти с **{member.guild.name}",
                color = disnake.Color.red(),
                timestamp = datetime.now())
        
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
                name="👥 Участников",
                value=f"Теперь нас: **{len(member.guild.members)}**",
                inline=True)
        
        return embed
    
    async def add_user_to_database(self, member: disnake.Member):
        user = UserCreate(
            ds_id = member.id,
            nickname = member.name,
            avatar_url = member.avatar.url if member.avatar else "",
            created_at = member.created_at.isoformat(),
            message_count = 1,
            level = 1,
            guild_id = member.guild.id
        )

        async with async_session_factory() as session:
            async with session.begin():
                user_service = UserService(session)
                await user_service.add_new_user(user)

    async def delete_user_from_database(self, member: disnake.Member):
        async with async_session_factory() as session:
                async with session.begin():
                    user_service = UserService(session)
                    await user_service.delete_user(member.id)


    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        if member.bot:
            return
        
        try:
            welcome_channel = member.guild.system_channel
            if welcome_channel:
                async with async_session_factory() as session:
                    async with session.begin():
                        guild_service = GuildService(session)
                        message = await guild_service.get_welcome_message(member.guild.id)
                        if message and message.welcome_message:
                            formatted_message = self.format_welcome_message(message.welcome_message, member, member.guild)
                            embed = await self.create_welcome_embed(member, formatted_message)
                            await welcome_channel.send(embed=embed)
                        else:
                            embed = await self.create_welcome_embed(member, None)
                            await welcome_channel.send(embed=embed)
            await self.add_user_to_database(member)
        except Exception as e:
            print(f"Ошибка при приветствии {member.name} на {member.guild.name}: {e}")


    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        if member.bot:
            return
        
        welcome_channel = member.guild.system_channel

        if welcome_channel:
            embed = await self.create_remove_embed(member)
            await welcome_channel.send(embed=embed)

        await self.delete_user_from_database(member)

def setup(bot: commands.Bot):
    bot.add_cog(MemberLeaveJoin(bot))