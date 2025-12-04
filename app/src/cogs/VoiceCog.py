import disnake
from disnake.ext import commands

class VoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_delete_channels = set()

    @commands.slash_command(name="create_voice", description="Создать голосовой канал")
    async def create_voice(self, inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(description="Название канала"),
        user_limit: int = commands.Param(0, description="Лимит пользователей (0 = без лимита)")):
        try:
            voice_channel = await inter.guild.create_voice_channel(
                name = name,
                user_limit = user_limit,
                category = inter.channel.category,
                reason = f"Создано пользователем {inter.author}"
            )

            self.auto_delete_channels.add(voice_channel.id)

            await inter.response.send_message(
                f"Голосовой канал {voice_channel.mention} создан",
                ephemeral = True
            )
        except Exception as e:
            await inter.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
     if before.channel and before.channel.id in self.auto_delete_channels:
         if len(before.channel.members) == 0:
            try:
                await before.channel.delete(reason="Автоматическое удаление пустого канала")
                self.auto_delete_channels.discard(before.channel.id)
                print(f"🗑️ Удалён пустой канал: {before.channel.name}")
            except Exception as e:
                print(f"❌ Ошибка при удалении канала: {e}")


def setup(bot):
    bot.add_cog(VoiceCog(bot))