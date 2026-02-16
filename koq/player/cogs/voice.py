import asyncio
import os
import re
import discord
from discord.ext import commands
from pathlib import Path
import yt_dlp

from koq.player.queue import PlayingQueue

ytdlp_opts = {
    "format": "bestaudio",
    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
    "outtmpl": "tmp/%(title)s.%(ext)s",
}


# Create a class for the audio cog
class AudioCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.volumeControl = None
        self.queues: dict[int, PlayingQueue] = {}

    @commands.Cog.listener()
    # Cogが読み込まれた時に発動
    async def on_ready(self):
        print("VoiceCog on ready!")

    # Function to join a voice channel
    async def join_voice_channel(self, ctx: commands.Context):
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            return await channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")

    # Function to play music
    async def play_music(self, ctx: commands.Context, url: str):
        voice_client: discord.VoiceClient = None
        try:
            voice_client = discord.utils.get(
                self.bot.voice_clients, guild=ctx.guild
            )

            # If bot is not already in a voice channel, join the caller's channel
            if not voice_client or not voice_client.is_connected():
                voice_client = await self.join_voice_channel(ctx)

            # Fetch video info
            if os.path.exists(url.replace("\\", "/")):
                url2 = url
                title = Path(url).name
            elif "storage.koq.jp" in url:
                title, url2 = await self.storageServerHandler(ctx, url)
            else:
                title, url2 = await self.generalHandler(ctx, url)

            if title is None or url2 is None:
                await ctx.send("An error occurred while playing the song.")
                # Clean up: disconnect if no queue exists and nothing is playing
                if (ctx.guild.id not in self.queues or len(self.queues.get(ctx.guild.id, [])) == 0) and voice_client:
                    await voice_client.disconnect()
                return

            # Add to queue or play immediately
            if ctx.guild.id in self.queues:
                self.queues[ctx.guild.id].append(
                    url=url2, title=title, requester=ctx.author.name
                )
                await ctx.send(f"**{title}** has been added to the queue.")
            else:
                self.queues[ctx.guild.id] = PlayingQueue()
                self.queues[ctx.guild.id].append(
                    url=url2, title=title, requester=ctx.author.name
                )
                await self.play_next(ctx)
        except Exception as e:
            print(e)
            await ctx.send("An error occurred while playing the song.")
            # Clean up: disconnect if no queue exists and nothing is playing
            if (ctx.guild.id not in self.queues or len(self.queues.get(ctx.guild.id, [])) == 0) and voice_client:
                await voice_client.disconnect()
            elif ctx.guild.id in self.queues:
                await self.play_next(ctx)

    # Function to play next song in queue
    async def play_next(self, ctx: commands.Context):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if (
            ctx.guild.id in self.queues
            and self.queues[ctx.guild.id]
            and len(self.queues[ctx.guild.id]) >= 1
        ):
            queue = self.queues[ctx.guild.id].pop()
            await ctx.send(f"Now playing **{queue.title}**")
            vol_trans = discord.PCMVolumeTransformer(
                original=discord.FFmpegPCMAudio(queue.url), volume=0.1
            )
            voice_client.play(vol_trans)
            while voice_client.is_paused() or voice_client.is_playing():
                await asyncio.sleep(1)
            await self.play_next(ctx)
        else:
            await ctx.send("No more songs in queue.")
            self.queues.pop(ctx.guild.id)
            await voice_client.disconnect()

    @commands.hybrid_command(name="q")
    async def ambiguous_q(self, ctx: commands.Context):
        await ctx.send("ambiguous command, To stop bot, may use `stop` or to show queue, may use `queue`.")

    # Play command
    @commands.hybrid_command(name="play", help="Plays a song", aliases=["p"])
    async def play(self, ctx: commands.Context, url: str):
        if ctx.interaction:
            await ctx.defer()
        if ctx.message:
            await ctx.message.add_reaction("✅")
        await self.play_music(ctx, url)

    # Pause command
    @commands.hybrid_command(name="pause", help="Pauses a song")
    async def pause(self, ctx: commands.Context):
        if ctx.message:
            await ctx.message.add_reaction("✅")
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("Music paused.")
        else:
            await ctx.send("No song is currently playing.")

    # Resume command
    @commands.hybrid_command(name="resume", help="Resumes a song")
    async def resume(self, ctx: commands.Context):
        if ctx.message:
            await ctx.message.add_reaction("✅")
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Music resumed.")
        else:
            await ctx.send("No song is currently paused.")

    # Queue command
    @commands.hybrid_command(name="queue", help="Show song queues")
    async def queue(self, ctx: commands.Context):
        await ctx.send(
            f"```{self.queues.get(ctx.guild.id)}```"
            if self.queues.get(ctx.guild.id)
            else "No songs in queue."
        )

    @commands.hybrid_command(name="volume", help="Set volume", aliases=["vol"])
    async def volume(self, ctx: commands.Context, volume: str):
        if ctx.voice_client is None or not ctx.voice_client.is_connected():
            return await ctx.send("Not connected to a voice channel.")
        elif float(volume) < 0 or float(volume) > 1:
            return await ctx.send("Volume must be between 0 and 1.")
        ctx.voice_client.source.volume = float(volume)
        await ctx.send(f"Volume set to {volume}")

    # Skip command
    @commands.hybrid_command(name="skip", help="Skips the current song", aliases=["next", "s"])
    async def skip(self, ctx: commands.Context):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Skipping the current song...")
        else:
            await ctx.send("No song is currently playing.")

    # Stop command
    @commands.hybrid_command(
        name="stop",
        help="Stops the music and clears the queue",
        aliases=["leave", "quit"],
    )
    async def stop(self, ctx: commands.Context):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
        self.queues.pop(ctx.guild.id)
        await voice_client.disconnect()
        await ctx.send("Music stopped and queue cleared.")

    async def generalHandler(self, ctx: commands.Context, url: str):
        with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
            try:
                info = ydl.extract_info(
                    url,
                    download=False,
                )
            except yt_dlp.DownloadError:
                await ctx.send("Invalid URL.")
                return None, None
            except Exception as e:
                print(f"General handler error: {e}")
                await ctx.send("An error occurred while processing the URL.")
                return None, None

            try:
                filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".m4a"
                title = info["title"]
                if not os.path.exists(filename):
                    ydl.extract_info(
                        url,
                        download=True,
                    )
            except Exception as e:
                print(f"Download error: {e}")
                await ctx.send("An error occurred while downloading the audio.")
                return None, None
                
        return title, filename

    async def storageServerHandler(self, ctx: commands.Context, url: str):
        if "storage.koq.jp" in url and not url.endswith("/download"):
            url = url.removesuffix("/") + "/download"
        else:
            await ctx.send("Invalid URL.")
            return None, None

        with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
            try:
                title = (
                    re.search(
                        r"(?<=https:\/\/storage\.koq\.jp\/s\/)[a-zA-Z0-9]+(?=\/download)",
                        url,
                    ).group(0)
                    + ".m4a"
                )
                ydl.extract_info(
                    url,
                    download=True,
                )
                os.rename("tmp/download.m4a", "tmp/" + title)

            except yt_dlp.DownloadError:
                await ctx.send("Invalid URL.")
                return None, None
            except Exception as e:
                print(f"Storage server error: {e}")
                await ctx.send("An error occurred while downloading from storage server.")
                return None, None

        return title, "tmp/" + title


async def setup(bot: commands.Bot):
    await bot.add_cog(AudioCog(bot))  # Add the AudioCog to the bot as a cog
