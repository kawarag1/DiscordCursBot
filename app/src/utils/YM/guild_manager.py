from disnake import VoiceChannel, TextChannel
from app.src.utils.YM.voice_manager import VoiceManager

class GuildsManager:
    def __init__(self):
        self.guilds: dict = {}

    async def get_guild(self, voice_channel: VoiceChannel, text_channel: TextChannel):
        guild_id = voice_channel.guild.id

        if guild_id in self.guilds:
            return self.guilds[guild_id]
        else:
            vm = VoiceManager(voice_channel, text_channel)
            await self.add_guild(guild_id, vm)
            return vm

    async def add_guild(self, guild_id: int, vm: VoiceManager):
        if guild_id not in self.guilds:
            self.guilds[guild_id] = vm

    async def delete_guild(self, guild_id: int):
        if guild_id in self.guilds:
            del self.guilds[guild_id]