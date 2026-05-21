import disnake
import math
from disnake.ext import commands

from app.src.cogs.CheckCog import CommandCheckCog
from app.src.orm.database.database import async_session_factory
from app.src.services.user_service import UserService

class LevelCog(CommandCheckCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def create_embed(self, message:disnake.Message, level: int):
        embed = disnake.Embed(
            title = "Повышение уровня!",
            description = f"{message.author.mention} получил {level} уровень!")
        return embed


    async def count_message(self, message: disnake.Message, guild: disnake.Guild):
        async with async_session_factory() as session:
            async with session.begin():
                user_service = UserService(session)
                profile = await user_service.get_server_profile(message.author.id)
                print(profile)
                profile.message_count += 1
                level = math.sqrt(profile.message_count)
                if level.is_integer():
                    profile.level = int(level)
                    await user_service.change_server_profile(profile)

                    welcome_channel = guild.system_channel
                    if welcome_channel:
                        embed = await self.create_embed(message, profile.level)
                        await welcome_channel.send(embed=embed)
                else:
                    await user_service.change_server_profile(profile)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return
        await self.count_message(message, message.guild)
                            

    @commands.slash_command(name="level", description="Проверить свой уровень")
    async def check_level(self, inter: disnake.ApplicationCommandInteraction):
        async with async_session_factory() as session:
                async with session.begin():
                    user_service = UserService(session)
                    profile = await user_service.get_server_profile(inter.user.id)
                    await inter.response.send_message(f"Ваш уровень: {profile.level}")


def setup(bot:commands.Bot):
    bot.add_cog(LevelCog(bot))
