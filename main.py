import disnake
# from create_link import CreatePaymentLink
from disnake.ext import commands
import math
import os

from app.src.services.server_profile_service import ServerProfileService
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



@bot.slash_command(name="ping", description="Проверить работу бота")
async def ping(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message(f"Pong {round(bot.latency * 1000)}мс")



# @bot.event
# async def on_message(message: disnake.Message):
#     if message.author.bot:
#         return
#     else:
#         async with async_session_factory() as session:
#             async with session.begin():
#                 profile_service = ServerProfileService(session)
#                 profile = await profile_service.get_server_profile(message.author.id)
#                 profile.message_count += 1
#                 level = math.sqrt(profile.message_count)
#                 if level.is_integer():
#                     profile.level = int(level)
#                     await profile_service.change_server_profile(profile)


#                     welcome_channel_id = 1403031110971031756
#                     welcome_channel = bot.get_channel(welcome_channel_id)
#                     if welcome_channel:
#                         embed = disnake.Embed(
#                             title = "Повышение уровня!",
#                             description = f"{message.author.mention} получил {profile.level} уровень!",
#                         )
#                         await welcome_channel.send(embed=embed)

#                 else:
#                     await profile_service.change_server_profile(profile)



@bot.slash_command(name="level", description="Проверить свой уровень")
async def check_level(inter: disnake.ApplicationCommandInteraction):
     async with async_session_factory() as session:
            async with session.begin():
                profile_service = ServerProfileService(session)
                profile = await profile_service.get_server_profile(inter.user.id)
                await inter.response.send_message(f"Ваш уровень: {profile.level}")
    

@bot.slash_command(name="create_voice", description="Создать голосовой канал")
async def create_voice(inter: disnake.ApplicationCommandInteraction,
    name: str = commands.Param(description="Название канала"),
    user_limit: int = commands.Param(0, description="Лимит пользователей (0 = без лимита)")):
    try:
        voice_channel = await inter.guild.create_voice_channel(
            name = name,
            user_limit = user_limit,
            category = inter.channel.category,
            reason = f"Создано пользователем {inter.author}"
        )

        auto_delete_channels.add(voice_channel.id)

        await inter.response.send_message(
            f"Голосовой канал {voice_channel.mention} создан",
            ephemeral = True
        )
    except Exception as e:
        await inter.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)



@bot.event
async def on_voice_state_update(member, before, after):
     if before.channel and before.channel.id in auto_delete_channels:
         if len(before.channel.members) == 0:
            try:
                await before.channel.delete(reason="Автоматическое удаление пустого канала")
                auto_delete_channels.discard(before.channel.id)
                print(f"🗑️ Удалён пустой канал: {before.channel.name}")
            except Exception as e:
                print(f"❌ Ошибка при удалении канала: {e}")

bot.run(token)