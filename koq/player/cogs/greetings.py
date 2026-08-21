import discord
from discord.ext import commands  # Bot Commands Frameworkをインポート
from loguru import logger


class GreetingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    # Cogが読み込まれた時に発動
    async def on_ready(self):
        logger.info("GreetingsCog on ready!")

    @commands.hybrid_command(name="hello", aliases=["hi", "hey"])
    async def hello(self, ctx: commands.Context, *, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f"Hello {member.name}~")
        else:
            await ctx.send(f"Hello {member.name}... This feels familiar.")
        self._last_member = member


async def setup(bot):
    await bot.add_cog(
        GreetingsCog(bot)
    )  # GreetingsCogにBotを渡してインスタンス化し、Botにコグとして登録する
