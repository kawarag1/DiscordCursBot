import disnake
from app.src.utils.YM.track import Track
from disnake import Message, VoiceChannel, VoiceClient, TextChannel


class VoiceManager:
    def __init__(self, voice_channel: VoiceChannel, text_channel: TextChannel):
        self.voice_channel: VoiceChannel = voice_channel
        self.text_channel: TextChannel = text_channel
        self.voice_client: VoiceClient = None
        self.message: Message = None
        self.counter: int = 0
        self.queue: list = []

    async def connect(self):
        """Подключение к голосовому чату"""
        if self.voice_client and self.voice_client.is_connected():
            return

        guild_voice_client = getattr(self.voice_channel.guild, 'voice_client', None)
        if guild_voice_client and guild_voice_client.is_connected():
            self.voice_client = guild_voice_client
            return

        try:
            self.voice_client = await self.voice_channel.connect()
        except disnake.errors.ClientException as e:
            if 'Already connected to a voice channel' in str(e):
                guild_voice_client = getattr(self.voice_channel.guild, 'voice_client', None)
                if guild_voice_client and guild_voice_client.is_connected():
                    self.voice_client = guild_voice_client
                    return
            raise

    async def disconnect(self):
        """Отключение от голосового чата"""
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None

    async def first_track(self):
        if isinstance(self.queue[0], Track):
            return self.queue[0]
        else:
            return self.queue[0].tracks[0]

    async def skip(self, playlist: bool = False):
        if not playlist:
            if isinstance(self.queue[0], Track):
                del self.queue[0]
            else:
                if len(self.queue[0].tracks) > 0:
                    del self.queue[0].tracks[0]
                else:
                    del self.queue[0]
        else:
            del self.queue[0]

    async def delete_message(self):
        try:
            await self.message.delete()
        except Exception:
            pass

    async def play(self):
        """Воспроизведение трека"""
        pass