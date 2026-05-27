from yandex_music import ClientAsync
from app.src.settings.settings import settings
import asyncio

client = asyncio.run(ClientAsync(settings.YM_TOKEN).init())
client.request.set_timeout(30)