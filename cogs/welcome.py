import discord
from discord.ext import commands
from discord import app_commands
from database import get_guild, update_guild, ensure_guild, get_db
from utils.embeds import success_embed, error_embed, base_embed
from utils.checks import has_manage_guild
from config import PINK, PURPLE, EMOJIS


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _format_message(self, message: str, member: discord.Member) -> str:
        return (
            message
            .replace("{user}", member.mention)
            .replace("{username}", str(member))
            .replace("{server}", member.guild.name)
            .replace("{count}", str(member.guild.member_count))
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_data = get_guild(member.guild.id)
        if not guild_data:
            return

        if guild_data.get("autoroles"):
            pass

        with get_db() as conn:
            autoroles = conn.execute(
                "SELECT role_id FROM autoroles WHERE guild_id = ?",
                (member.guild.id,)
            ).fetchall()
        for row in autoroles:
            role = member.guild.get_role(row["role_id"])
            if role:
                try:
                    await member.add_roles(role, reason="Auto-role on join")
                except discord.Forbidden:
                    pass

        if guild_data.get("welcome_enabled") and guild_data.get("welcome_channel"):
            channel = member.guild.get_channel(guild_data["welcome_channel"])
            if channel:
                msg = guild_data.get("welcome_message") or f"Welcome {member.mention} to **{member.guild.name}**! 🌸 You're member #{member.guild.member_count}!"
                embed = base_embed(
                    title=f"{EMOJIS['welcome']} Welcome!",
                    description=self._format_message(msg, member),
                    color=PINK,
                    thumbnail=member.display_avatar.url,
                )
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_data = get_guild(member.guild.id)
        if not guild_data:
            return
        if guild_data.get("goodbye_enabled") and guild_data.get("goodbye_channel"):
            channel = member.guild.get_channel(guild_data["goodbye_channel"])
            if channel:
                msg = guild_data.get("goodbye_message") or f"**{member}** has left the server. Goodbye! 👋"
                embed = base_embed(
                    title="👋 Goodbye!",
                    description=self._format_message(msg, member),
                    color=PURPLE,
                    thumbnail=member.display_avatar.url,
                )
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.premium_since is None and after.premium_since is not None:
            guild_data = get_guild(after.guild.id)
            if guild_data and guild_data.get("boost_channel"):
                channel = after.guild.get_channel(guild_data["boost_channel"])
                if channel:
                    msg = guild_data.get("boost_message") or f"💖 **{after.mention}** just boosted the server! Thank you so much!"
                    embed = base_embed(
                        title="🚀 Server Boost!",
                        description=msg,
                        color=0xF47FFF,
                        thumbnail=after.display_avatar.url,
                    )
                    await channel.send(embed=embed)

    welcome_group = app_commands.Group(name="welcome", description="Welcome system configuration")

    @welcome_group.command(name="setup", description="Set up the welcome system")
    @has_manage_guild()
    @app_commands.describe(channel="Channel to send welcome messages", message="Welcome message (use {user}, {username}, {server}, {count})")
    async def welcome_setup(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = None):
        ensure_guild(interaction.guild_id)
        update_guild(interaction.guild_id, welcome_channel=channel.id, welcome_enabled=1, welcome_message=message)
        embed = success_embed("Welcome System Enabled", f"Welcome messages will be sent to {channel.mention}!\n\n**Variables:** `{{user}}`, `{{username}}`, `{{server}}`, `{{count}}`")
        await interaction.response.send_message(embed=embed)

    @welcome_group.command(name="disable", description="Disable the welcome system")
    @has_manage_guild()
    async def welcome_disable(self, interaction: discord.Interaction):
        ensure_guild(interaction.guild_id)
        update_guild(interaction.guild_id, welcome_enabled=0)
        await interaction.response.send_message(embed=success_embed("Welcome Disabled", "Welcome messages have been turned off."))

    @welcome_group.command(name="test", description="Send a test welcome message")
    @has_manage_guild()
    async def welcome_test(self, interaction: discord.Interaction):
        await self.on_member_join(interaction.user)
        await interaction.response.send_message(embed=success_embed("Test Sent", "A test welcome message has been triggered!"), ephemeral=True)

    goodbye_group = app_commands.Group(name="goodbye", description="Goodbye system configuration")

    @goodbye_group.command(name="setup", description="Set up the goodbye system")
    @has_manage_guild()
    @app_commands.describe(channel="Channel for goodbye messages", message="Goodbye message")
    async def goodbye_setup(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = None):
        ensure_guild(interaction.guild_id)
        update_guild(interaction.guild_id, goodbye_channel=channel.id, goodbye_enabled=1, goodbye_message=message)
        await interaction.response.send_message(embed=success_embed("Goodbye System Enabled", f"Goodbye messages will be sent to {channel.mention}!"))

    @goodbye_group.command(name="disable", description="Disable the goodbye system")
    @has_manage_guild()
    async def goodbye_disable(self, interaction: discord.Interaction):
        ensure_guild(interaction.guild_id)
        update_guild(interaction.guild_id, goodbye_enabled=0)
        await interaction.response.send_message(embed=success_embed("Goodbye Disabled", "Goodbye messages have been turned off."))

    autorole_group = app_commands.Group(name="autorole", description="Auto-role system")

    @autorole_group.command(name="add", description="Add a role to auto-assign on join")
    @has_manage_guild()
    @app_commands.describe(role="Role to auto-assign")
    async def autorole_add(self, interaction: discord.Interaction, role: discord.Role):
        ensure_guild(interaction.guild_id)
        with get_db() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO autoroles (guild_id, role_id) VALUES (?, ?)",
                (interaction.guild_id, role.id)
            )
        await interaction.response.send_message(embed=success_embed("Auto-role Added", f"{role.mention} will now be given to new members automatically!"))

    @autorole_group.command(name="remove", description="Remove an auto-role")
    @has_manage_guild()
    @app_commands.describe(role="Role to remove from auto-roles")
    async def autorole_remove(self, interaction: discord.Interaction, role: discord.Role):
        with get_db() as conn:
            conn.execute("DELETE FROM autoroles WHERE guild_id = ? AND role_id = ?", (interaction.guild_id, role.id))
        await interaction.response.send_message(embed=success_embed("Auto-role Removed", f"{role.mention} removed from auto-roles."))

    @autorole_group.command(name="list", description="List all auto-roles")
    async def autorole_list(self, interaction: discord.Interaction):
        with get_db() as conn:
            rows = conn.execute("SELECT role_id FROM autoroles WHERE guild_id = ?", (interaction.guild_id,)).fetchall()
        if not rows:
            await interaction.response.send_message(embed=error_embed("No Auto-roles", "No auto-roles configured."))
            return
        roles = [interaction.guild.get_role(r["role_id"]) for r in rows]
        desc = "\n".join(r.mention for r in roles if r)
        await interaction.response.send_message(embed=base_embed(title="🎀 Auto-roles", description=desc, color=PINK))

    @app_commands.command(name="boostmessage", description="Configure the boost message")
    @has_manage_guild()
    @app_commands.describe(channel="Boost announce channel", message="Boost message")
    async def boostmessage(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = None):
        ensure_guild(interaction.guild_id)
        update_guild(interaction.guild_id, boost_channel=channel.id, boost_message=message)
        await interaction.response.send_message(embed=success_embed("Boost Message Set", f"Boost notifications will be sent to {channel.mention}!"))

    @app_commands.command(name="membercount", description="Show the member count")
    async def membercount(self, interaction: discord.Interaction):
        guild = interaction.guild
        humans = sum(1 for m in guild.members if not m.bot)
        bots = guild.member_count - humans
        embed = base_embed(
            title=f"👥 {guild.name} Members",
            color=PINK,
        )
        embed.add_field(name="Total", value=f"**{guild.member_count:,}**", inline=True)
        embed.add_field(name="Humans", value=f"**{humans:,}**", inline=True)
        embed.add_field(name="Bots", value=f"**{bots:,}**", inline=True)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
