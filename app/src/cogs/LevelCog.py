import disnake
import math
from disnake.ext import commands

from app.src.services.server_profile_service import ServerProfileService
from app.src.orm.database.database import async_session_factory

class LevelCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.welcome_channel_id = 1403031110971031756

    async def create_embed(self, message:disnake.Message, level: int):
        embed = disnake.Embed(
            title = "Повышение уровня!",
            description = f"{message.author.mention} получил {level} уровень!")
        return embed


    async def count_message(self, message: disnake.Message):
        async with async_session_factory() as session:
            async with session.begin():
                profile_service = ServerProfileService(session)
                profile = await profile_service.get_server_profile(message.author.id)
                profile.message_count += 1
                level = math.sqrt(profile.message_count)
                if level.is_integer():
                    profile.level = int(level)
                    await profile_service.change_server_profile(profile)

                    welcome_channel = self.bot.get_channel(self.welcome_channel_id)
                    if welcome_channel:
                        embed = await self.create_embed(message, profile.level)
                        await welcome_channel.send(embed=embed)
                else:
                    await profile_service.change_server_profile(profile)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return
        await self.count_message(message)
                        

def setup(bot:commands.Bot):
    bot.add_cog(LevelCog(bot))
