import disnake
# from create_link import CreatePaymentLink
from disnake.ext import commands
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.src.schemas.request.server_user_schema import ServerUserCreate
from app.src.schemas.request.user_for_delete_schema import UserForDelete
from app.src.schemas.request.user_schema import UserCreate
from app.src.services.server_profile_service import ServerProfileService
from app.src.services.user_service import UserService
from app.src.settings.settings import settings
from app.src.orm.database.database import create_tables, async_session_factory, run_migrations

token = settings.TOKEN

print(token)



bot = commands.Bot(
    command_prefix = "!",
    intents = disnake.Intents.all(),
    activity = disnake.Game("Тестовый бот")
)

@bot.event
async def on_ready():
    await create_tables()
    print(f"{bot.user} is activated!")

@bot.event
async def on_member_join(member: disnake.Member):
    if member.bot:
        return
    else:
        welcome_channel_id = 1403031110971031756
        welcome_channel = bot.get_channel(welcome_channel_id)

        if welcome_channel:
            embed = disnake.Embed(
                title = "ЙООООООООУ",
                description = f"мы приветсвуем тебя, {member.mention}, ты пришёл на **{member.guild.name}",

                color = disnake.Color.red(),
                timestamp = datetime.now()
                )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(
                name="👥 Участников",
                value=f"Теперь нас: **{len(member.guild.members)}**",
                inline=True
            )
            embed.add_field(
                name="📅 Дата регистрации",
                value=f"<t:{int(member.created_at.timestamp())}:D>",
                inline=True
            )
            embed.set_footer(text="Приятного общения!")
        
            await welcome_channel.send(embed=embed)

        user = UserCreate(
            ds_id = member.id,
            nickname = member.name,
            avatar_url = member.avatar.url if member.avatar else "",
            tag = member.tag,
            created_at = member.created_at.isoformat()
        )

        user_profile = ServerUserCreate(
            ds_id = member.id,
            server_nickname = member.display_name,
            message_count = 1,
            level = 1
        )

        async with async_session_factory() as session:
            async with session.begin():
                user_service = UserService(session)
                await user_service.add_new_user(user)


        async with async_session_factory() as session:
            async with session.begin():
                server_profile_service = ServerProfileService(session)
                await server_profile_service.add_new_server_profile(user_profile)

@bot.event
async def on_member_remove(member: disnake.Member):
    if member.bot:
        return
    else:
        welcome_channel_id = 1403031110971031756
        welcome_channel = bot.get_channel(welcome_channel_id)

        if welcome_channel:
            embed = disnake.Embed(
                title = "Плохие новости",
                description = f"{member.mention}, решил уйти с **{member.guild.name}",

                color = disnake.Color.red(),
                timestamp = datetime.now()
                )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(
                name="👥 Участников",
                value=f"Теперь нас: **{len(member.guild.members)}**",
                inline=True
            )
        
            await welcome_channel.send(embed=embed)

            async with async_session_factory() as session:
                async with session.begin():
                    profile_service = ServerProfileService(session)
                    await profile_service.delete_server_profile(member.id)

            async with async_session_factory() as session:
                async with session.begin():
                    user_service = UserService(session)
                    await user_service.delete_user(member.id)


@bot.slash_command(name="ping", description="Проверить работу бота")
async def ping(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message(f"Pong {round(bot.latency * 1000)}мс")



@bot.event
async def on_message(message: disnake.Message):
    pass

bot.run(token)