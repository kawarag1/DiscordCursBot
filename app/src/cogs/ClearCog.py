import disnake
from disnake.ext import commands

from app.src.cogs.CheckCog import CommandCheckCog

class ClearCog(CommandCheckCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="clear", description="Очистить сообщения в канале")
    async def clear_messages(self, inter: disnake.ApplicationCommandInteraction,
        amount: int = commands.Param(..., description="Количество сообщений для удаления")):
        if not inter.author.guild_permissions.manage_messages:
            await inter.response.send_message("❌ У вас нет прав на управление сообщениями.", ephemeral=True)
            return

        if amount <= 0:
            await inter.response.send_message("❌ Количество должно быть положительным числом.", ephemeral=True)
            return
        
        if amount > 100:
            await inter.response.send_message("❌ Можно удалить не более 100 сообщений за раз.", ephemeral=True)
            return
        
        await inter.response.defer(ephemeral=True)

        deleted = await inter.channel.purge(limit=amount)

        await inter.edit_original_response(content=f"✅ Удалено {len(deleted)} сообщений.")

def setup(bot):
    bot.add_cog(ClearCog(bot))
