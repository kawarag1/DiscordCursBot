import disnake
from disnake.ext import commands

from app.src.services.member_logs import MemberLogs

class MemberLogsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        if member.bot:
            return
        guild = member.guild
        log_channel = disnake.utils.get(guild.text_channels, name = "members")
        if log_channel:
            try:
                embed = await MemberLogs.create_join_embed(member)
                await log_channel.send(embed = embed)
            except Exception as e:
                print(f"❌ Ошибка при логгировании: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member,):
        if member.bot:
            return
        guild = member.guild
        log_channel = disnake.utils.get(guild.text_channels, name = "members")
        if log_channel:
            try:
                embed = await MemberLogs.create_leave_embed(member)
                await log_channel.send(embed = embed)
            except Exception as e:
                print(f"❌ Ошибка при логгировании: {e}")
                
def setup(bot: commands.Bot):
    bot.add_cog(MemberLogsCog(bot))