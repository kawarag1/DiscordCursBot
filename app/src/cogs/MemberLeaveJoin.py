import disnake
from disnake.ext import commands
from datetime import datetime

from app.src.services.user_service import UserService
from app.src.orm.database.database import async_session_factory
from app.src.schemas.request.user_schema import UserCreate

class MemberLeaveJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    async def create_welcome_embed(self, member: disnake.Member) -> disnake.Embed:
        embed = disnake.Embed(
            title = "Добро пожаловать!",
            description = f"мы приветсвуем тебя, {member.mention}, ты пришёл на **{member.guild.name}",
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
    async def on_member_join(self, member: disnake.Member, guild: disnake.Guild):
        if member.bot:
            return
        

        welcome_channel = guild.system_channel

        if welcome_channel:
            embed = await self.create_welcome_embed(member)
            await welcome_channel.send(embed=embed)

        await self.add_user_to_database(member)


    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member, guild: disnake.Guild):
        if member.bot:
            return
        
        welcome_channel = guild.system_channel

        if welcome_channel:
            embed = await self.create_remove_embed(member)
            await welcome_channel.send(embed=embed)

        await self.delete_user_from_database(member)

def setup(bot: commands.Bot):
    bot.add_cog(MemberLeaveJoin(bot))