import disnake
from disnake.ext import commands
import os
from fastapi import FastAPI

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


app = FastAPI(
    title="API для управления подписками на бота",
    description="Этот API позволяет управлять подписками на бота, включая создание, обновление и удаление подписок.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)