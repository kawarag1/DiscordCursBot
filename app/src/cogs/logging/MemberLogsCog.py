import disnake
from disnake.ext import commands

from app.src.services.member_logs import MemberLogs

class MemberLogsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log_channel_id = 1446055029290303488


    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        if member.bot:
            return
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = await MemberLogs.create_join_embed(member)
                await log_channel.send(embed = embed)
            except Exception as e:
                print(f"❌ Ошибка при логгировании: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        if member.bot:
            return
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = await MemberLogs.create_leave_embed(member)
                await log_channel.send(embed = embed)
            except Exception as e:
                print(f"❌ Ошибка при логгировании: {e}")
                
def setup(bot: commands.Bot):
    bot.add_cog(MemberLogsCog(bot))