import disnake
from disnake.ext import commands

from app.src.services.command_service import CommandService
from app.src.orm.database.database import async_session_factory
from app.src.schemas.request.disable_command_schema import DisableCommandSchema

class CommandCheckCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def cog_check(self, inter: disnake.ApplicationCommandInteraction) -> bool:
        print(f"🔍 [cog_check] Команда: {inter.application_command.name}")
        
        if not inter.guild:
            return True
        
        command_name = inter.application_command.name
        
        if command_name == "ping":
            return True
        
        try:
            async with async_session_factory() as session:
                async with session.begin():
                    is_enabled = await CommandService(session).check_command(
                        DisableCommandSchema(
                            guild_id=inter.guild.id,
                            command_name=command_name
                        )
                    )
                    
                    print(f"   → Результат: {'✅ ВКЛЮЧЕНА' if is_enabled else '❌ ОТКЛЮЧЕНА'}")
                    
                    if not is_enabled:
                        if not inter.response.is_done():
                            await inter.response.send_message(
                                f"❌ Команда `/{command_name}` отключена на этом сервере.",
                                ephemeral=True
                            )
                        return False
                    
                    return True
                    
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

    async def cog_before_slash_command_invoke(self, inter: disnake.ApplicationCommandInteraction):
        print(f"🔍 [cog_before_invoke] Команда: {inter.application_command.name}")
        
        if not await self.cog_check(inter):
            raise commands.CommandError("Команда отключена")

def setup(bot):
    pass