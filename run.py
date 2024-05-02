import asyncio
from discord.ext import commands  # Bot Commands Frameworkをインポート
import discord
from koq.player.config import settings

INITIAL_EXTENSIONS = ["greetings", "voice"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("//"), intents=intents)

print(
    discord.utils.oauth_url(
        client_id=settings.client_id,
        permissions=discord.Permissions(permissions=8),
        scopes=["bot"],
    )
)


async def main():
    async with bot:
        for cog in INITIAL_EXTENSIONS:
            await bot.load_extension(f"koq.player.cogs.{cog}")
        await bot.start(settings.token)


async def load_extensions(bot):
    for ext in INITIAL_EXTENSIONS:
        try:
            await bot.load_extension(f"koq.player.cogs.{ext}")
        except Exception as e:
            print(f"Failed to load extension {ext}.")
            e.with_traceback()


asyncio.run(main())
