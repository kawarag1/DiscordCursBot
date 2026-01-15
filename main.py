import disnake
# from create_link import CreatePaymentLink
from disnake.ext import commands
import os

from app.src.settings.settings import settings

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



@bot.slash_command(name="ping", description="Проверить работу бота")
async def ping(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message(f"Pong {round(bot.latency * 1000)}мс")    

bot.run(token)