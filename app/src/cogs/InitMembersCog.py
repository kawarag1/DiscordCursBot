import disnake
from disnake.ext import commands

from app.src.orm.database.database import migrate, async_session_factory
from app.src.orm.database.repo.guilds_repo import GuildsRepository
from app.src.schemas.request.user_schema import UserCreate
from app.src.services.action_service import ActionService
from app.src.services.command_service import CommandService
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
        async with async_session_factory() as session:
            async with session.begin():
                action_service = ActionService(session)
                user_service = UserService(session)
                command_service = CommandService(session)
                guild_repo = GuildsRepository(session)
                

                await action_service.clear_actions(guild.id)
                await command_service.clear_disabled_commands(guild.id)
                await guild_repo.delete_message_attachments(guild.id)
                await guild_repo.delete_messages(guild.id)
                await user_service.clear_users(guild.id)
                await guild_repo.delete_by_id(guild.id)
                await session.commit()
            

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
                        warnings = 0,
                        guild_id = member.guild.id
                    )
                    user_service = UserService(session)
                    await user_service.add_new_user(user)

                print("✅ Инициализация завершена!")
            
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
                content="✅ Участники сервера успешно инициализированы!"
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
                    warnings = 0,
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
                    warnings = 0,
                    guild_id = member.guild.id
                )
                await user_service.add_new_user(new_user)

    async def setup_logs(self, guild: disnake.Guild):
        try:
            existing_category = disnake.utils.get(guild.categories, name="logs")
            
            if existing_category:
                category = existing_category
                print(f"📁 Категория 'logs' уже существует на сервере {guild.name}")
            else:
                category = await guild.create_category(
                    name="logs",
                    reason="Бот: Создание лог-каналов для администраторов"
                )
                print(f"📁 Категория 'logs' создана на сервере {guild.name}")
            
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
            
            await category.edit(overwrites=overwrites)
            
            messages_channel = disnake.utils.get(category.text_channels, name="messages")
            if not messages_channel:
                messages_channel = await guild.create_text_channel(
                    name="messages",
                    category=category,
                    reason="Бот: Создание канала для логов сообщений"
                )
                await messages_channel.edit(overwrites=overwrites)
                print(f"📝 Создан канал 'messages' на сервере {guild.name}")
            
            members_channel = disnake.utils.get(category.text_channels, name="members")
            if not members_channel:
                members_channel = await guild.create_text_channel(
                    name="members",
                    category=category,
                    reason="Бот: Создание канала для логов участников"
                )
                await members_channel.edit(overwrites=overwrites)
                print(f"👥 Создан канал 'members' на сервере {guild.name}")
            
            mod_log_channel = disnake.utils.get(category.text_channels, name="mod-log")
            if not mod_log_channel:
                mod_log_channel = await guild.create_text_channel(
                    name="mod-log",
                    category=category,
                    reason="Бот: Создание канала для логов модерации"
                )
                await mod_log_channel.edit(overwrites=overwrites)
                print(f"�️ Создан канал 'mod-log' на сервере {guild.name}")
            
            print(f"✅ Лог-каналы настроены на сервере {guild.name}")
            return category, messages_channel, members_channel
            
        except disnake.Forbidden:
            print(f"❌ Нет прав для создания/изменения каналов на сервере {guild.name}")
        except Exception as e:
            print(f"❌ Ошибка при создании/проверке каналов на {guild.name}: {e}")

def setup(bot):
    bot.add_cog(InitMembersCog(bot))