import asyncio

import discord
from discord.ext import commands  # Bot Commands Frameworkをインポート

from koq.player.config import settings

INITIAL_EXTENSIONS = ["greetings", "voice"]


class KoqBot(commands.Bot):
    async def setup_hook(self) -> None:
        for cog in INITIAL_EXTENSIONS:
            await self.load_extension(f"koq.player.cogs.{cog}")

        guild_id = settings.get("guild_id")
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"Synced slash commands to guild: {guild_id}")
        else:
            await self.tree.sync()
            print("Synced global slash commands.")


intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True
intents.voice_states = True
intents.message_content = True
bot = KoqBot(command_prefix="//", intents=intents)

print(
    discord.utils.oauth_url(
        client_id=settings.client_id,
        permissions=discord.Permissions(
            view_channel=True,
            send_messages=True,
            add_reactions=True,
            connect=True,
            speak=True,
        ),
        scopes=["bot", "applications.commands"],
    )
)


async def main():
    await bot.start(settings.token)


asyncio.run(main())
