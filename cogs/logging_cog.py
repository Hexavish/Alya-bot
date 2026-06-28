import discord
from discord.ext import commands
from discord import app_commands
from database import get_guild, update_guild, ensure_guild
from utils.embeds import base_embed
from utils.checks import has_manage_guild
from config import PINK, PURPLE, ERROR_COLOR, SUCCESS_COLOR, WARNING_COLOR, EMOJIS


class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_log(self, guild: discord.Guild, embed: discord.Embed):
        guild_data = get_guild(guild.id)
        if not guild_data or not guild_data.get("log_channel"):
            return
        channel = guild.get_channel(guild_data["log_channel"])
        if channel:
            try:
                await channel.send(embed=embed)
            except Exception:
                pass

    @app_commands.command(name="setlog", description="Set the logging channel 📋")
    @has_manage_guild()
    @app_commands.describe(channel="Channel to send logs to")
    async def setlog(self, interaction: discord.Interaction, channel: discord.TextChannel):
        ensure_guild(interaction.guild_id)
        update_guild(interaction.guild_id, log_channel=channel.id)
        from utils.embeds import success_embed
        await interaction.response.send_message(embed=success_embed("Log Channel Set", f"Logs will be sent to {channel.mention}!"))

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        embed = base_embed(title=f"{EMOJIS['ban']} Member Banned", color=ERROR_COLOR)
        embed.add_field(name="User", value=f"{user} (`{user.id}`)", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        await self.send_log(guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        embed = base_embed(title="👋 Member Left", description=f"{member.mention} left the server.", color=WARNING_COLOR)
        embed.add_field(name="User", value=f"{member} (`{member.id}`)", inline=True)
        embed.add_field(name="Roles", value=" ".join(r.mention for r in member.roles[1:][:5]) or "None", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await self.send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        embed = base_embed(title="🗑️ Message Deleted", color=ERROR_COLOR)
        embed.add_field(name="Author", value=f"{message.author.mention}", inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Content", value=message.content[:1024] or "*Empty*", inline=False)
        await self.send_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        embed = base_embed(title="✏️ Message Edited", color=WARNING_COLOR)
        embed.add_field(name="Author", value=before.author.mention, inline=True)
        embed.add_field(name="Channel", value=before.channel.mention, inline=True)
        embed.add_field(name="Before", value=before.content[:512] or "*Empty*", inline=False)
        embed.add_field(name="After", value=after.content[:512] or "*Empty*", inline=False)
        await self.send_log(before.guild, embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        embed = base_embed(title="➕ Channel Created", color=SUCCESS_COLOR)
        embed.add_field(name="Channel", value=f"{channel.mention} (`{channel.id}`)", inline=True)
        embed.add_field(name="Type", value=str(channel.type).title(), inline=True)
        await self.send_log(channel.guild, embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        embed = base_embed(title="➖ Channel Deleted", color=ERROR_COLOR)
        embed.add_field(name="Channel", value=f"`#{channel.name}` (`{channel.id}`)", inline=True)
        await self.send_log(channel.guild, embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        embed = base_embed(title="🎭 Role Created", color=SUCCESS_COLOR)
        embed.add_field(name="Role", value=f"{role.mention} (`{role.id}`)", inline=True)
        await self.send_log(role.guild, embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        embed = base_embed(title="🎭 Role Deleted", color=ERROR_COLOR)
        embed.add_field(name="Role", value=f"`@{role.name}` (`{role.id}`)", inline=True)
        await self.send_log(role.guild, embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel == after.channel:
            return
        if after.channel and not before.channel:
            action, color = f"joined **{after.channel.name}**", SUCCESS_COLOR
        elif before.channel and not after.channel:
            action, color = f"left **{before.channel.name}**", ERROR_COLOR
        else:
            action, color = f"moved from **{before.channel.name}** → **{after.channel.name}**", WARNING_COLOR
        embed = base_embed(title="🎙️ Voice Update", description=f"{member.mention} {action}", color=color)
        await self.send_log(member.guild, embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Logging(bot))
