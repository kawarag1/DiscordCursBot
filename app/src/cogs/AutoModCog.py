import asyncio
from datetime import datetime
import json
import re

import disnake
from disnake.ext import commands
from pathlib import Path

from app.src.orm.database.database import async_session_factory
from app.src.schemas.request.action_schema import ActionSchema
from app.src.services.action_service import ActionService
from app.src.services.user_service import UserService

class AutoModCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bad_words = []
        self.settings = {}


    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_config()
        print(f"{self.bot.user} is ready and AutoModCog is loaded!")

    async def load_config(self):
        try:
            config_path = Path(__file__).parent.parent / "utils" / "bad_words.json"
            with open(config_path, "r") as f:
                data = json.load(f)
                self.bad_words = data.get("bad_words", [])
                self.settings = data.get("settings", {})
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            self.bad_words = []
            self.settings = {"max_warnings": 3, "delete_message": True, "warn_user": True, "kick_user": False, "ban_user": False}
                
    async def contains_bad_word(self, message: disnake.Message):
        content = message.content.lower()
        for word in self.bad_words:
            pattern = r'\b' + re.escape(word.lower()) + r'\b'
            if re.search(pattern, content):
                return True
        return False

    async def get_log_channel(self, guild: disnake.Guild):
        logs_category = disnake.utils.get(guild.categories, name="logs")
        if logs_category:
            return disnake.utils.get(logs_category.text_channels, name="mod-log")
        return None
    
    async def log_action_to_ds_channel(self, guild: disnake.Guild, embed: disnake.Embed):
        log_channel = await self.get_log_channel(guild)
        if log_channel:
            await log_channel.send(embed=embed)

    async def warn_user(self, message: disnake.Message):
        async with async_session_factory() as session:
            async with session.begin():
                user_service = UserService(session)
                warnings = await user_service.add_warning(message.author.id)
                if warnings >= self.settings.get("max_warnings", 3):
                    if self.settings.get("mute_user", True):
                        try:
                            async with async_session_factory() as session:
                                async with session.begin():
                                    action_service = ActionService(session)
                                    user_service = UserService(session)
                                    user_id = await user_service.get_userID_by_DS_ID(message.author.id)
                                    await action_service.log_action(
                                        ActionSchema(
                                            guild_id=message.guild.id,
                                            user_id=user_id,
                                            action="mute",
                                            reason="Превышение допустимого количества предупреждений",
                                            target_id=user_id,
                                            details=f"Автоматический мут за превышение количества предупреждений",
                                            created_at=datetime.utcnow()
                                        )
                                    )
                        except Exception as e:
                            print(f"❌ Ошибка при логировании мута: {e}")
                        await self.mute_user(message.guild, message.author, reason="Превышение количества предупреждений")
                        await message.channel.send(f"⚠️ {message.author.mention}, вы были замучены за превышение количества предупреждений.", delete_after=10)
                else:
                    await message.channel.send(f"⚠️ {message.author.mention}, данное слово запрещено! Это предупреждение {warnings}/{self.settings.get('max_warnings', 3)}.\nПожалуйста, соблюдайте правила сервера.", delete_after=10)
                

    async def mute_user(self, guild: disnake.Guild, user: disnake.Member, reason: str):
        mute_role = disnake.utils.get(guild.roles, name="Muted")
        if not mute_role:
            mute_role = await guild.create_role(
                name="Muted",
                reason="Создание роли для мута"
            )
            for channel in guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
        
        await user.add_roles(mute_role, reason=reason)

        duration = self.settings.get("mute_duration", 60)
        duration_minutes = duration // 60
        duration_hours = duration_minutes // 60
        if duration_hours > 0:
            duration_text = f"{duration_hours} час(ов)"
        elif duration_minutes > 0:
            duration_text = f"{duration_minutes} минут"
        else:
            duration_text = f"{duration} секунд"
        
        embed = disnake.Embed(
            title="🔇 Пользователь замучен",
            description=f"**Пользователь:** {user.mention}\n"
                       f"**ID:** {user.id}\n"
                       f"**Причина:** {reason}\n"
                       f"**Длительность:** {duration_text}\n"
                       f"**Модератор:** Бот (автоматически)",
            color=disnake.Color.red(),
            timestamp=datetime.utcnow()
        )
        await self.log_action_to_ds_channel(guild, embed)

        async def unmute():
            await asyncio.sleep(duration)
            await user.remove_roles(mute_role, reason="Срок мута истёк")
            
            
            unmute_embed = disnake.Embed(
                title="🔊 Срок мута истёк",
                description=f"**Пользователь:** {user.mention}\n"
                           f"**Длительность:** {duration_text}",
                color=disnake.Color.green(),
                timestamp=datetime.utcnow()
            )
            await self.log_action_to_ds_channel(guild, unmute_embed)
        
        
        asyncio.create_task(unmute())
        
        return mute_role



    @commands.slash_command(name="warnings", description="Просмотреть количество предупреждений пользователя")
    async def view_warnings(self, interaction: disnake.ApplicationCommandInteraction):
        async with async_session_factory() as session:
            async with session.begin():
                user_service = UserService(session)
                warnings = await user_service.get_user_warnings(interaction.author.id)
                await interaction.response.send_message(f"⚠️ {interaction.author.mention} имеет {warnings} предупреждений.")

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return
        url_pattern = re.compile(r'https?://\S+', re.IGNORECASE)

        contains = await self.contains_bad_word(message)
        if contains:
            if self.settings.get("warn_user", True):
                await self.warn_user(message)
                try:
                    async with async_session_factory() as session:
                        async with session.begin():
                            action_service = ActionService(session)
                            user_service = UserService(session)
                            user_id = await user_service.get_userID_by_DS_ID(message.author.id)
                            await action_service.log_action(
                                ActionSchema(
                                    guild_id=message.guild.id,
                                    user_id=user_id,
                                    action="warn",
                                    reason="Использование запрещённого слова",
                                    target_id=user_id,
                                    details=f"Автоматическое предупреждение",
                                    created_at=datetime.utcnow()
                                )
                            )
                except Exception as e:
                    print(f"❌ Ошибка при логировании предупреждения: {e}")

            if self.settings.get("delete_message", True):
                try:
                    await message.delete()
                except Exception as e:
                    print(f"Ошибка при удалении сообщения: {e}")
            return
            
        
        if url_pattern.search(message.content):
            try:
                await message.delete()
                await message.channel.send(
                    f"❌ {message.author.mention}, ссылки запрещены на этом сервере!",
                    delete_after=5
                )
            except Exception as e:
                print(f"Ошибка при удалении сообщения со ссылкой: {e}")

def setup(bot: commands.Bot):
    bot.add_cog(AutoModCog(bot))