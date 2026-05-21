from datetime import datetime
import disnake
from disnake.ext import commands

class WelcomeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def create_welcome_embed(self) -> disnake.Embed:
        embed = disnake.Embed(
            title="🎉 Бот добавлен на сервер!",
            description="Приветствую! Спасибо за добавление меня на ваш сервер!",
            color=disnake.Color.green(),
            timestamp=datetime.now()
        )

        embed.add_field(
            name="📋 Начало работы",
            value="• Используйте `/help` чтобы увидеть все команды",
            inline=False
        )

        return embed
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
        welcome_channel = guild.system_channel
        if welcome_channel:
            embed = await self.create_welcome_embed()
            await welcome_channel.send(embed = embed)

def setup(bot):
    bot.add_cog(WelcomeCog(bot))
    


