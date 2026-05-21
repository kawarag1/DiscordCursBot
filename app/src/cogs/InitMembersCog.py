import disnake
from disnake.ext import commands

from app.src.orm.database.database import migrate, async_session_factory
from app.src.orm.database.repo.guilds_repo import GuildsRepository
from app.src.schemas.request.user_schema import UserCreate
from app.src.services.guild_service import GuildService
from app.src.services.user_service import UserService

class InitMembersCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        await migrate()
        print(f"{self.bot.user} is activated!")
            

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
        await self.setup_logs(guild)
        async with async_session_factory() as session:
                async with session.begin():
                    guild_service = GuildService(session)
                    guild_check = await guild_service.check_guild_by_id(guild.id)
                    if guild_check:
                        print("True")
                    else:
                        await guild_service.add_new_guild(guild)
                        await self.initialize_guild_members(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Guild):
        for member in guild.members:
            if not member.bot:
                async with async_session_factory() as session:
                    async with session.begin():
                        user_service = UserService(session)
                        await user_service.delete_user(member.id)
        async with async_session_factory() as session:
            guild_repo = GuildsRepository(session)
            await guild_repo.delete_by_id(guild.id)

    async def initialize_guild_members(self, guild: disnake.Guild):
        if not guild:
            print("Сервер не найден")
            return 

        print(f"🔄 Начинаю инициализацию участников сервера: {guild.name}")
        async with async_session_factory() as session:
            try:
                members = [member async for member in guild.fetch_members(limit=None)]
                for member in members:                    
                    user = UserCreate(
                        ds_id = member.id,
                        nickname = member.name,
                        avatar_url = member.avatar.url if member.avatar else "",
                        created_at = member.created_at.isoformat(),
                        message_count = 1,
                        level = 1,
                        guild_id = member.guild.id
                    )
                    user_service = UserService(session)
                    await user_service.add_new_user(user)

                print(f"✅ Инициализация завершена!")
            
            except Exception as e:
                await session.rollback()
                print(f"❌ Ошибка инициализации: {e}")

    @commands.slash_command(name="initialize", description="Принудительно инициализировать участников сервера")
    @commands.has_permissions(administrator=True)
    async def init_members(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)

        try:
            await self.initialize_guild_members(inter.guild)
            await inter.edit_original_response(
                content=f"✅ Участники сервера успешно инициализированы!"
            )
        except Exception as e:
            await inter.edit_original_response(
                content=f"❌ Ошибка инициализации: {str(e)[:100]}"
            )
    
    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        await self.add_or_update_member(after)


    async def add_or_update_member(self, member: disnake.Member):
        async with async_session_factory() as session:
            user_service = UserService(session)
            user = await user_service.get_server_profile(member.id)
            if user:
                new_user = UserCreate(
                    ds_id = member.id,
                    nickname = member.name,
                    avatar_url = member.avatar.url if member.avatar else "",
                    created_at = member.created_at.isoformat(),
                    message_count = 1,
                    level = 1,
                    guild_id = member.guild.id
                )
                
                await user_service.change_server_profile(new_user)
            else:
                new_user = UserCreate(
                    ds_id = member.id,
                    nickname = member.name,
                    avatar_url = member.avatar.url if member.avatar else "",
                    created_at = member.created_at.isoformat(),
                    message_count = 1,
                    level = 1,
                    guild_id = member.guild.id
                )
                await user_service.add_new_user(new_user)

    async def setup_logs(self, guild: disnake.Guild):
        try:
            existing_category = disnake.utils.get(guild.categories, name="logs")
            
            if existing_category:
                print(f"📁 Категория 'logs' уже существует на сервере {guild.name}")
                
                messages_channel = disnake.utils.get(existing_category.text_channels, name="messages")
                members_channel = disnake.utils.get(existing_category.text_channels, name="members")
                
                if not messages_channel:
                    messages_channel = await guild.create_text_channel(
                        name="messages",
                        category=existing_category,
                        reason="Бот: Создание недостающего канала для логов сообщений"
                    )
                    print(f"📝 Создан недостающий канал 'messages' на сервере {guild.name}")
                
                if not members_channel:
                    members_channel = await guild.create_text_channel(
                        name="members",
                        category=existing_category,
                        reason="Бот: Создание недостающего канала для логов участников"
                    )
                    print(f"👥 Создан недостающий канал 'members' на сервере {guild.name}")
                
                overwrites = {
                    guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                }
                
                for role in guild.roles:
                    if role.permissions.administrator:
                        overwrites[role] = disnake.PermissionOverwrite(
                            view_channel=True,
                            read_messages=True,
                            send_messages=True,
                            read_message_history=True 
                        )
                
                await existing_category.edit(overwrites=overwrites)
                if messages_channel:
                    await messages_channel.edit(overwrites=overwrites)
                if members_channel:
                    await members_channel.edit(overwrites=overwrites)
                
                print(f"✅ Права доступа обновлены для существующих лог-каналов на сервере {guild.name}")
                return existing_category, messages_channel, members_channel
            
            overwrites = {
                guild.default_role: disnake.PermissionOverwrite(view_channel=False),
            }
            
            for role in guild.roles:
                if role.permissions.administrator:
                    overwrites[role] = disnake.PermissionOverwrite(
                        view_channel=True,
                        read_messages=True,
                        send_messages=True,
                        read_message_history=True 
                    )
            
            category = await guild.create_category(
                name="logs",
                overwrites=overwrites,
                reason="Бот: Создание лог-каналов для администраторов"
            )
            
            messages_channel = await guild.create_text_channel(
                name="messages",
                category=category,
                reason="Бот: Канал для логов сообщений"
            )
            
            members_channel = await guild.create_text_channel(
                name="members",
                category=category,
                reason="Бот: Канал для логов участников"
            )
            
            print(f"✅ Категория 'logs' и каналы созданы на сервере {guild.name}")
            
        except disnake.Forbidden:
            print(f"❌ Нет прав для создания/изменения каналов на сервере {guild.name}")
        except Exception as e:
            print(f"❌ Ошибка при создании/проверке каналов на {guild.name}: {e}")

def setup(bot):
    bot.add_cog(InitMembersCog(bot))