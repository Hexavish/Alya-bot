import discord
from discord.ext import commands
from discord import app_commands
from database import get_guild, update_guild, ensure_guild, get_db
from utils.embeds import base_embed, success_embed, error_embed
from utils.checks import has_manage_guild
from config import PINK, PURPLE, SUCCESS_COLOR, ERROR_COLOR, EMOJIS


class Suggestions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="suggest", description="Submit a suggestion 💡")
    @app_commands.describe(suggestion="Your suggestion")
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        guild_data = get_guild(interaction.guild_id)
        if not guild_data or not guild_data.get("suggestion_channel"):
            await interaction.response.send_message(embed=error_embed("Not Configured", "The suggestion system hasn't been set up yet!"), ephemeral=True)
            return
        channel = interaction.guild.get_channel(guild_data["suggestion_channel"])
        if not channel:
            await interaction.response.send_message(embed=error_embed("Channel Not Found", "Suggestion channel no longer exists!"), ephemeral=True)
            return
        with get_db() as conn:
            count = conn.execute("SELECT COUNT(*) as c FROM suggestions WHERE guild_id = ?", (interaction.guild_id,)).fetchone()["c"] + 1
        embed = base_embed(
            title=f"💡 Suggestion #{count}",
            description=suggestion,
            color=PURPLE,
            author=interaction.user,
        )
        embed.add_field(name="Status", value="⏳ Pending", inline=True)
        await interaction.response.send_message(embed=success_embed("Suggestion Submitted!", "Your suggestion has been submitted! 💡"), ephemeral=True)
        msg = await channel.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        with get_db() as conn:
            conn.execute(
                "INSERT INTO suggestions (guild_id, user_id, suggestion, message_id) VALUES (?, ?, ?, ?)",
                (interaction.guild_id, interaction.user.id, suggestion, msg.id)
            )

    suggest_setup = app_commands.Group(name="suggestion", description="Suggestion system settings")

    @suggest_setup.command(name="setup", description="Set up the suggestion channel")
    @has_manage_guild()
    @app_commands.describe(channel="Channel for suggestions")
    async def suggestion_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        ensure_guild(interaction.guild_id)
        update_guild(interaction.guild_id, suggestion_channel=channel.id)
        await interaction.response.send_message(embed=success_embed("Suggestion System Set!", f"Suggestions will be posted in {channel.mention}!"))

    @suggest_setup.command(name="approve", description="Approve a suggestion")
    @has_manage_guild()
    @app_commands.describe(suggestion_id="Suggestion ID to approve", reason="Reason for approval")
    async def suggestion_approve(self, interaction: discord.Interaction, suggestion_id: int, reason: str = "Looks good!"):
        with get_db() as conn:
            s = conn.execute("SELECT * FROM suggestions WHERE id = ? AND guild_id = ?", (suggestion_id, interaction.guild_id)).fetchone()
        if not s:
            await interaction.response.send_message(embed=error_embed("Not Found", "Suggestion not found!"), ephemeral=True)
            return
        with get_db() as conn:
            conn.execute("UPDATE suggestions SET status = 'approved' WHERE id = ?", (suggestion_id,))
        guild_data = get_guild(interaction.guild_id)
        if guild_data and guild_data.get("suggestion_channel") and s["message_id"]:
            ch = interaction.guild.get_channel(guild_data["suggestion_channel"])
            if ch:
                try:
                    msg = await ch.fetch_message(s["message_id"])
                    embed = base_embed(title=f"💡 Suggestion #{suggestion_id} — ✅ Approved", description=s["suggestion"], color=SUCCESS_COLOR)
                    embed.add_field(name="Status", value=f"✅ Approved by {interaction.user.mention}\n> {reason}", inline=False)
                    await msg.edit(embed=embed)
                except Exception:
                    pass
        await interaction.response.send_message(embed=success_embed("Suggestion Approved!", f"Suggestion #{suggestion_id} has been approved."))

    @suggest_setup.command(name="deny", description="Deny a suggestion")
    @has_manage_guild()
    @app_commands.describe(suggestion_id="Suggestion ID to deny", reason="Reason for denial")
    async def suggestion_deny(self, interaction: discord.Interaction, suggestion_id: int, reason: str = "Not suitable at this time."):
        with get_db() as conn:
            s = conn.execute("SELECT * FROM suggestions WHERE id = ? AND guild_id = ?", (suggestion_id, interaction.guild_id)).fetchone()
        if not s:
            await interaction.response.send_message(embed=error_embed("Not Found", "Suggestion not found!"), ephemeral=True)
            return
        with get_db() as conn:
            conn.execute("UPDATE suggestions SET status = 'denied' WHERE id = ?", (suggestion_id,))
        guild_data = get_guild(interaction.guild_id)
        if guild_data and guild_data.get("suggestion_channel") and s["message_id"]:
            ch = interaction.guild.get_channel(guild_data["suggestion_channel"])
            if ch:
                try:
                    msg = await ch.fetch_message(s["message_id"])
                    embed = base_embed(title=f"💡 Suggestion #{suggestion_id} — ❌ Denied", description=s["suggestion"], color=ERROR_COLOR)
                    embed.add_field(name="Status", value=f"❌ Denied by {interaction.user.mention}\n> {reason}", inline=False)
                    await msg.edit(embed=embed)
                except Exception:
                    pass
        await interaction.response.send_message(embed=success_embed("Suggestion Denied", f"Suggestion #{suggestion_id} has been denied."))


async def setup(bot: commands.Bot):
    await bot.add_cog(Suggestions(bot))
