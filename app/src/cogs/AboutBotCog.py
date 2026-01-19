import disnake
from disnake.ext import commands

class AboutBotCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="about", description="Информация о боте")
    async def about(self, interaction):
        embed = disnake.Embed(
            title=f"🤖 О боте {self.bot.user.name}",
            description="Многофункциональный Discord бот",
            color=disnake.Color.gold()
        )
        
        embed.add_field(name="Версия", value="alpha 0.0.1", inline=True)
        embed.add_field(name="Разработчик", value="kawarag1", inline=True)
        embed.add_field(name="Библиотека", value="Disnake", inline=True)
        embed.add_field(name="Серверов", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Задержка", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        embed.set_footer(text="Спасибо за использование!")
        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="help",description="Показать все команды бота")
    async def help_command(self, interaction: disnake.ApplicationCommandInteraction):
        
        embed = disnake.Embed(
            title="📚 Команды бота",
            description=f"Привет! Я **{self.bot.user.name}** - полезный бот для управления сервером.\n\n"
                       f"Всего команд: **3**\n"
                       f"Используйте `/` для вызова команд",
            color=disnake.Color.blurple(),
            timestamp=interaction.created_at
        )
        
        embed.add_field(
            name="🧹 `/clear`",
            value="**Описание:** Очищает тестовые сообщения в чате (до 100 штук)\n"
                  "**Использование:** `/clear [количество=10]`\n"
                  "**Требуемые права:** Управление сообщениями",
            inline=False
        )
        
        embed.add_field(
            name="🔊 `/create_voice`",
            value="**Описание:** Создает голосовой канал с указанными параметрами\n"
                  "**Параметры:**\n"
                  "• `name` - Название канала\n"
                  "• `amount` - Максимальное количество участников\n"
                  "**Использование:** `/create_voice name: General amount: 10`",
            inline=False
        )
        
        embed.add_field(
            name="🏓 `/ping`",
            value="**Описание:** Проверяет задержку бота и его работоспособность\n"
                  "**Использование:** `/ping`\n"
                  "**Показывает:** Задержку API Discord",
            inline=False
        )
        await interaction.response.send_message(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(AboutBotCog(bot))