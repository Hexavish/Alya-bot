import discord
from datetime import datetime
from config import PINK, PURPLE, SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR, INFO_COLOR, BOT_NAME, EMOJIS


def base_embed(
    title: str = "",
    description: str = "",
    color: int = PINK,
    footer: str = None,
    thumbnail: str = None,
    image: str = None,
    author: discord.Member | discord.User | None = None,
) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow(),
    )
    if footer:
        embed.set_footer(text=footer, icon_url=None)
    else:
        embed.set_footer(text=f"{BOT_NAME} • Cute but powerful 🌸")
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    if author:
        embed.set_author(name=str(author), icon_url=author.display_avatar.url)
    return embed


def success_embed(title: str, description: str = "") -> discord.Embed:
    return base_embed(
        title=f"{EMOJIS['success']} {title}",
        description=description,
        color=SUCCESS_COLOR,
    )


def error_embed(title: str, description: str = "") -> discord.Embed:
    return base_embed(
        title=f"{EMOJIS['error']} {title}",
        description=description,
        color=ERROR_COLOR,
    )


def warning_embed(title: str, description: str = "") -> discord.Embed:
    return base_embed(
        title=f"{EMOJIS['warning']} {title}",
        description=description,
        color=WARNING_COLOR,
    )


def info_embed(title: str, description: str = "") -> discord.Embed:
    return base_embed(
        title=f"{EMOJIS['info']} {title}",
        description=description,
        color=INFO_COLOR,
    )


def mod_embed(action: str, target: discord.Member, moderator: discord.Member, reason: str, color: int = PURPLE) -> discord.Embed:
    embed = base_embed(
        title=f"{EMOJIS['mod']} {action}",
        color=color,
    )
    embed.add_field(name="Target", value=f"{target.mention} (`{target.id}`)", inline=True)
    embed.add_field(name="Moderator", value=f"{moderator.mention}", inline=True)
    embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    return embed
