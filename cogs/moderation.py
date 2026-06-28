import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from database import add_warning, get_warnings, update_guild, ensure_guild
from utils.embeds import success_embed, error_embed, mod_embed, base_embed
from utils.checks import has_mod_permissions, has_manage_guild
from utils.helpers import parse_time, format_time
from config import PINK, PURPLE, ERROR_COLOR, EMOJIS


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban a member from the server")
    @has_mod_permissions()
    @app_commands.describe(member="Member to ban", reason="Reason for the ban", delete_days="Days of messages to delete")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided", delete_days: int = 0):
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(embed=error_embed("Cannot Ban", "You can't ban someone with equal or higher role!"), ephemeral=True)
            return
        try:
            await member.send(embed=base_embed(title=f"{EMOJIS['ban']} Banned", description=f"You were banned from **{interaction.guild.name}**\n**Reason:** {reason}", color=ERROR_COLOR))
        except Exception:
            pass
        await member.ban(reason=f"{interaction.user} | {reason}", delete_message_days=delete_days)
        await interaction.response.send_message(embed=mod_embed("Member Banned", member, interaction.user, reason, ERROR_COLOR))

    @app_commands.command(name="unban", description="Unban a user by ID")
    @has_mod_permissions()
    @app_commands.describe(user_id="User ID to unban", reason="Reason for unban")
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user, reason=reason)
            await interaction.response.send_message(embed=success_embed("Member Unbanned", f"**{user}** has been unbanned.\n**Reason:** {reason}"))
        except discord.NotFound:
            await interaction.response.send_message(embed=error_embed("Not Found", "This user is not banned or doesn't exist."), ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member from the server")
    @has_mod_permissions()
    @app_commands.describe(member="Member to kick", reason="Reason for the kick")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(embed=error_embed("Cannot Kick", "You can't kick someone with equal or higher role!"), ephemeral=True)
            return
        try:
            await member.send(embed=base_embed(title=f"{EMOJIS['kick']} Kicked", description=f"You were kicked from **{interaction.guild.name}**\n**Reason:** {reason}", color=ERROR_COLOR))
        except Exception:
            pass
        await member.kick(reason=f"{interaction.user} | {reason}")
        await interaction.response.send_message(embed=mod_embed("Member Kicked", member, interaction.user, reason, PURPLE))

    @app_commands.command(name="timeout", description="Timeout a member")
    @has_mod_permissions()
    @app_commands.describe(member="Member to timeout", duration="Duration (e.g. 10m, 1h, 1d)", reason="Reason")
    async def timeout_cmd(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
        seconds = parse_time(duration)
        if not seconds or seconds > 2419200:
            await interaction.response.send_message(embed=error_embed("Invalid Duration", "Use format like `10m`, `1h`, `7d`. Max 28 days."), ephemeral=True)
            return
        until = discord.utils.utcnow() + timedelta(seconds=seconds)
        await member.timeout(until, reason=f"{interaction.user} | {reason}")
        embed = mod_embed(f"Member Timed Out ({format_time(seconds)})", member, interaction.user, reason, PURPLE)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="untimeout", description="Remove a timeout from a member")
    @has_mod_permissions()
    @app_commands.describe(member="Member to untimeout")
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        await interaction.response.send_message(embed=success_embed("Timeout Removed", f"{member.mention}'s timeout has been removed."))

    @app_commands.command(name="mute", description="Mute a member (requires Muted role)")
    @has_mod_permissions()
    @app_commands.describe(member="Member to mute", reason="Reason")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await interaction.guild.create_role(name="Muted", color=discord.Color.dark_gray())
            for channel in interaction.guild.channels:
                try:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)
                except Exception:
                    pass
        await member.add_roles(muted_role, reason=reason)
        await interaction.response.send_message(embed=mod_embed(f"{EMOJIS['mute']} Member Muted", member, interaction.user, reason, PURPLE))

    @app_commands.command(name="unmute", description="Unmute a member")
    @has_mod_permissions()
    @app_commands.describe(member="Member to unmute")
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if muted_role and muted_role in member.roles:
            await member.remove_roles(muted_role)
            await interaction.response.send_message(embed=success_embed("Member Unmuted", f"{member.mention} has been unmuted."))
        else:
            await interaction.response.send_message(embed=error_embed("Not Muted", "This member is not muted."), ephemeral=True)

    @app_commands.command(name="warn", description="Warn a member")
    @has_mod_permissions()
    @app_commands.describe(member="Member to warn", reason="Reason for the warning")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        warn_id = add_warning(member.id, interaction.guild_id, interaction.user.id, reason)
        warnings = get_warnings(member.id, interaction.guild_id)
        embed = mod_embed(f"{EMOJIS['warn']} Member Warned (#{warn_id})", member, interaction.user, reason, PURPLE)
        embed.add_field(name="Total Warnings", value=str(len(warnings)), inline=True)
        try:
            await member.send(embed=base_embed(title="⚠️ Warning Received", description=f"You received a warning in **{interaction.guild.name}**\n**Reason:** {reason}", color=0xFFD700))
        except Exception:
            pass
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warnings", description="View warnings for a member")
    @has_mod_permissions()
    @app_commands.describe(member="Member to check warnings for")
    async def warnings_cmd(self, interaction: discord.Interaction, member: discord.Member):
        warnings = get_warnings(member.id, interaction.guild_id)
        if not warnings:
            await interaction.response.send_message(embed=success_embed("No Warnings", f"{member.mention} has no warnings! 🌸"))
            return
        embed = base_embed(title=f"⚠️ Warnings for {member}", color=PURPLE, thumbnail=member.display_avatar.url)
        for w in warnings[:10]:
            embed.add_field(
                name=f"#{w['id']} — {w['timestamp'][:10]}",
                value=f"**Reason:** {w['reason']}\n**Mod:** <@{w['moderator_id']}>",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="Clear messages in a channel")
    @has_mod_permissions()
    @app_commands.describe(amount="Number of messages to delete (1-100)", member="Only delete messages from this member")
    async def clear(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100], member: discord.Member = None):
        await interaction.response.defer(ephemeral=True)
        def check(msg):
            return not member or msg.author == member
        deleted = await interaction.channel.purge(limit=amount, check=check)
        await interaction.followup.send(embed=success_embed("Messages Cleared", f"Deleted **{len(deleted)}** messages{f' from {member.mention}' if member else ''}."), ephemeral=True)

    @app_commands.command(name="slowmode", description="Set channel slowmode")
    @has_mod_permissions()
    @app_commands.describe(seconds="Slowmode delay in seconds (0 to disable)")
    async def slowmode(self, interaction: discord.Interaction, seconds: app_commands.Range[int, 0, 21600]):
        await interaction.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await interaction.response.send_message(embed=success_embed("Slowmode Disabled", "Slowmode has been removed from this channel."))
        else:
            await interaction.response.send_message(embed=success_embed("Slowmode Set", f"Slowmode set to **{seconds}** seconds."))

    @app_commands.command(name="lock", description="Lock a channel")
    @has_mod_permissions()
    @app_commands.describe(channel="Channel to lock (defaults to current)", reason="Reason")
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel = None, reason: str = "No reason"):
        ch = channel or interaction.channel
        await ch.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message(embed=success_embed(f"{EMOJIS['lock']} Channel Locked", f"{ch.mention} has been locked.\n**Reason:** {reason}"))

    @app_commands.command(name="unlock", description="Unlock a channel")
    @has_mod_permissions()
    @app_commands.describe(channel="Channel to unlock", reason="Reason")
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel = None, reason: str = "No reason"):
        ch = channel or interaction.channel
        await ch.set_permissions(interaction.guild.default_role, send_messages=None)
        await interaction.response.send_message(embed=success_embed(f"{EMOJIS['unlock']} Channel Unlocked", f"{ch.mention} has been unlocked.\n**Reason:** {reason}"))

    @app_commands.command(name="nickname", description="Change a member's nickname")
    @has_mod_permissions()
    @app_commands.describe(member="Member to rename", nickname="New nickname (leave empty to reset)")
    async def nickname(self, interaction: discord.Interaction, member: discord.Member, nickname: str = None):
        await member.edit(nick=nickname)
        if nickname:
            await interaction.response.send_message(embed=success_embed("Nickname Changed", f"{member.mention}'s nickname set to **{nickname}**."))
        else:
            await interaction.response.send_message(embed=success_embed("Nickname Reset", f"{member.mention}'s nickname has been reset."))

    @app_commands.command(name="role", description="Add or remove a role from a member")
    @has_mod_permissions()
    @app_commands.describe(member="Member", role="Role to add or remove")
    async def role_cmd(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(embed=success_embed("Role Removed", f"Removed {role.mention} from {member.mention}."))
        else:
            await member.add_roles(role)
            await interaction.response.send_message(embed=success_embed("Role Added", f"Added {role.mention} to {member.mention}."))

    @app_commands.command(name="serverinfo", description="Show information about this server")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        embed = base_embed(title=f"🌸 {g.name}", color=PINK)
        embed.set_thumbnail(url=g.icon.url if g.icon else None)
        embed.add_field(name="Owner", value=f"<@{g.owner_id}>", inline=True)
        embed.add_field(name="Members", value=f"{g.member_count:,}", inline=True)
        embed.add_field(name="Channels", value=str(len(g.channels)), inline=True)
        embed.add_field(name="Roles", value=str(len(g.roles)), inline=True)
        embed.add_field(name="Boosts", value=str(g.premium_subscription_count), inline=True)
        embed.add_field(name="Created", value=f"<t:{int(g.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Verification", value=str(g.verification_level).title(), inline=True)
        embed.add_field(name="Server ID", value=str(g.id), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Show information about a user")
    @app_commands.describe(member="Member to view info about")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        roles = [r.mention for r in member.roles[1:]][:10]
        embed = base_embed(title=f"👤 {member}", color=PINK, thumbnail=member.display_avatar.url)
        embed.add_field(name="ID", value=str(member.id), inline=True)
        embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
        embed.add_field(name="Bot", value="Yes" if member.bot else "No", inline=True)
        embed.add_field(name="Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
        if roles:
            embed.add_field(name=f"Roles ({len(member.roles)-1})", value=" ".join(roles), inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
