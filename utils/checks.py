import discord
from discord import app_commands
from discord.ext import commands
from config import OWNER_IDS


def is_owner():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.id in OWNER_IDS:
            return True
        raise app_commands.CheckFailure("This command is restricted to bot owners.")
    return app_commands.check(predicate)


def has_mod_permissions():
    async def predicate(interaction: discord.Interaction) -> bool:
        member = interaction.user
        if isinstance(member, discord.Member):
            if member.guild_permissions.administrator:
                return True
            if member.guild_permissions.kick_members or member.guild_permissions.ban_members or member.guild_permissions.manage_messages:
                return True
        raise app_commands.CheckFailure("You need moderation permissions to use this command.")
    return app_commands.check(predicate)


def has_manage_guild():
    async def predicate(interaction: discord.Interaction) -> bool:
        member = interaction.user
        if isinstance(member, discord.Member):
            if member.guild_permissions.manage_guild or member.guild_permissions.administrator:
                return True
        raise app_commands.CheckFailure("You need **Manage Server** permission.")
    return app_commands.check(predicate)


def is_guild_owner():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild and interaction.user.id == interaction.guild.owner_id:
            return True
        raise app_commands.CheckFailure("Only the server owner can use this command.")
    return app_commands.check(predicate)
