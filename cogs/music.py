import discord
import yt_dlp
import asyncio
from collections import deque
from discord.ext import commands
from discord import app_commands
from utils.embeds import base_embed, success_embed, error_embed
from config import PINK, PURPLE, EMOJIS

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    "extract_flat": False,
    "noplaylist": True,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -filter:a 'volume=0.5'",
}


class MusicQueue:
    def __init__(self):
        self.queue: deque = deque()
        self.current: dict | None = None
        self.loop: bool = False

    def add(self, track: dict):
        self.queue.append(track)

    def next(self) -> dict | None:
        if self.loop and self.current:
            return self.current
        if self.queue:
            self.current = self.queue.popleft()
            return self.current
        self.current = None
        return None

    def clear(self):
        self.queue.clear()
        self.current = None


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: dict[int, MusicQueue] = {}

    def get_queue(self, guild_id: int) -> MusicQueue:
        if guild_id not in self.queues:
            self.queues[guild_id] = MusicQueue()
        return self.queues[guild_id]

    async def ensure_voice(self, interaction: discord.Interaction) -> discord.VoiceClient | None:
        if not interaction.user.voice:
            await interaction.response.send_message(embed=error_embed("Not in Voice", "Join a voice channel first!"), ephemeral=True)
            return None
        vc = interaction.guild.voice_client
        if vc and vc.channel != interaction.user.voice.channel:
            await vc.move_to(interaction.user.voice.channel)
        elif not vc:
            vc = await interaction.user.voice.channel.connect()
        return vc

    async def fetch_track(self, query: str) -> dict | None:
        loop = asyncio.get_event_loop()
        if not query.startswith("http"):
            query = f"ytsearch:{query}"
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
                if "entries" in data:
                    data = data["entries"][0]
                return {
                    "url": data.get("url"),
                    "title": data.get("title", "Unknown"),
                    "duration": data.get("duration", 0),
                    "webpage_url": data.get("webpage_url", ""),
                    "thumbnail": data.get("thumbnail"),
                }
        except Exception:
            return None

    def play_next(self, guild_id: int, vc: discord.VoiceClient):
        q = self.get_queue(guild_id)
        track = q.next()
        if track:
            source = discord.FFmpegPCMAudio(track["url"], **FFMPEG_OPTIONS)
            source = discord.PCMVolumeTransformer(source)
            vc.play(source, after=lambda e: self.bot.loop.call_soon_threadsafe(self.play_next, guild_id, vc))

    @app_commands.command(name="play", description="Play a song from YouTube 🎵")
    @app_commands.describe(query="Song name or YouTube URL")
    async def play(self, interaction: discord.Interaction, query: str):
        vc = await self.ensure_voice(interaction)
        if not vc:
            return
        await interaction.response.defer()
        track = await self.fetch_track(query)
        if not track:
            await interaction.followup.send(embed=error_embed("Not Found", "Couldn't find that song! Try a different search."))
            return
        q = self.get_queue(interaction.guild_id)
        q.add(track)
        if not vc.is_playing() and not vc.is_paused():
            track = q.next()
            if track:
                source = discord.FFmpegPCMAudio(track["url"], **FFMPEG_OPTIONS)
                source = discord.PCMVolumeTransformer(source)
                vc.play(source, after=lambda e: self.bot.loop.call_soon_threadsafe(self.play_next, interaction.guild_id, vc))
            embed = base_embed(title=f"{EMOJIS['music']} Now Playing", description=f"[{track['title']}]({track['webpage_url']})", color=PURPLE)
        else:
            embed = base_embed(title=f"{EMOJIS['music']} Added to Queue", description=f"[{track['title']}]({track['webpage_url']})\nPosition: **#{len(q.queue)}**", color=PINK)
        if track.get("thumbnail"):
            embed.set_thumbnail(url=track["thumbnail"])
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="pause", description="Pause the music ⏸️")
    async def pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message(embed=success_embed("Paused ⏸️", "Music has been paused."))
        else:
            await interaction.response.send_message(embed=error_embed("Not Playing", "Nothing is playing right now!"), ephemeral=True)

    @app_commands.command(name="resume", description="Resume the music ▶️")
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message(embed=success_embed("Resumed ▶️", "Music has been resumed."))
        else:
            await interaction.response.send_message(embed=error_embed("Not Paused", "Music isn't paused!"), ephemeral=True)

    @app_commands.command(name="skip", description="Skip the current song ⏭️")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message(embed=success_embed("Skipped ⏭️", "Skipped the current song!"))
        else:
            await interaction.response.send_message(embed=error_embed("Not Playing", "Nothing to skip!"), ephemeral=True)

    @app_commands.command(name="stop", description="Stop music and disconnect 🔇")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            q = self.get_queue(interaction.guild_id)
            q.clear()
            await vc.disconnect()
            await interaction.response.send_message(embed=success_embed("Stopped 🔇", "Disconnected from voice channel."))
        else:
            await interaction.response.send_message(embed=error_embed("Not Connected", "I'm not in a voice channel!"), ephemeral=True)

    @app_commands.command(name="queue", description="View the music queue 📋")
    async def queue_cmd(self, interaction: discord.Interaction):
        q = self.get_queue(interaction.guild_id)
        if not q.current and not q.queue:
            await interaction.response.send_message(embed=base_embed(title="📋 Queue", description="The queue is empty! Use `/play` to add songs. 🎵", color=PINK))
            return
        desc = ""
        if q.current:
            desc += f"**Now Playing:**\n🎵 {q.current['title']}\n\n"
        if q.queue:
            desc += "**Up Next:**\n"
            desc += "\n".join(f"`{i+1}.` {t['title']}" for i, t in enumerate(list(q.queue)[:10]))
            if len(q.queue) > 10:
                desc += f"\n*...and {len(q.queue) - 10} more*"
        embed = base_embed(title=f"{EMOJIS['music']} Music Queue", description=desc, color=PURPLE)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
