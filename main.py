import disnake
# from create_link import CreatePaymentLink
from disnake.ext import commands
import os

from app.src.services.guild_service import GuildService
from app.src.settings.settings import settings
from app.src.orm.database.database import create_tables, async_session_factory

token = settings.TOKEN

print(token)

auto_delete_channels = set()

bot = commands.Bot(
    command_prefix = "!",
    intents = disnake.Intents.all(),
    activity = disnake.Game("Тестовый бот")
)


for filename in os.listdir("./app/src/cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"app.src.cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    await create_tables()
    print(f"{bot.user} is activated!")
    for guild in bot.guilds:
        async with async_session_factory() as session:
            async with session.begin():
                guild_service = GuildService(session)
                guild_check = await guild_service.check_guild_by_id(guild.id)
                if guild_check:
                    print("True")
                else:
                    await guild_service.add_new_guild(guild)



@bot.slash_command(name="ping", description="Проверить работу бота")
async def ping(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message(f"Pong {round(bot.latency * 1000)}мс")    

bot.run(token)