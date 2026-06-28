import discord
import random
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from database import get_user, update_user, ensure_user, get_leaderboard
from utils.embeds import base_embed, success_embed
from utils.helpers import xp_for_level, level_from_xp, progress_bar, format_number
from utils.paginator import PaginatorView, chunk_list
from config import PINK, PURPLE, XP_PER_MESSAGE, XP_COOLDOWN, EMOJIS


class Leveling(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        user = get_user(message.author.id, message.guild.id)
        last_xp = user.get("last_xp")
        if last_xp:
            elapsed = (datetime.utcnow() - datetime.fromisoformat(last_xp)).total_seconds()
            if elapsed < XP_COOLDOWN:
                return
        xp_gain = random.randint(XP_PER_MESSAGE, XP_PER_MESSAGE * 2)
        old_level = user["level"]
        new_xp = user["xp"] + xp_gain
        new_level, current, needed = level_from_xp(new_xp)
        update_user(
            message.author.id, message.guild.id,
            xp=new_xp, level=new_level, last_xp=datetime.utcnow().isoformat()
        )
        if new_level > old_level:
            embed = base_embed(
                title=f"🎉 Level Up!",
                description=f"Congratulations {message.author.mention}!\nYou reached **Level {new_level}**! 🌸",
                color=PINK,
                thumbnail=message.author.display_avatar.url,
            )
            try:
                await message.channel.send(embed=embed)
            except Exception:
                pass

    @app_commands.command(name="level", description="Check your level and XP 📊")
    @app_commands.describe(member="Check another user's level")
    async def level_cmd(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        user = get_user(target.id, interaction.guild_id)
        level, current_xp, needed_xp = level_from_xp(user["xp"])
        bar = progress_bar(current_xp, needed_xp)
        embed = base_embed(
            title=f"📊 {target.display_name}'s Level",
            color=PINK,
            thumbnail=target.display_avatar.url,
        )
        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="Total XP", value=f"**{format_number(user['xp'])}**", inline=True)
        embed.add_field(name="Progress", value=f"{bar}\n`{format_number(current_xp)}/{format_number(needed_xp)}`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View the XP leaderboard 🏆")
    async def leaderboard(self, interaction: discord.Interaction):
        top = get_leaderboard(interaction.guild_id, limit=50)
        if not top:
            await interaction.response.send_message(embed=base_embed(title="🏆 Leaderboard", description="No data yet! Start chatting to earn XP! 🌸", color=PINK))
            return
        chunks = chunk_list(top, 10)
        pages = []
        medals = ["🥇", "🥈", "🥉"]
        for page_idx, chunk in enumerate(chunks):
            lines = []
            for i, u in enumerate(chunk):
                rank = page_idx * 10 + i + 1
                medal = medals[rank - 1] if rank <= 3 else f"`#{rank}`"
                member = interaction.guild.get_member(u["user_id"])
                name = member.display_name if member else f"<@{u['user_id']}>"
                lines.append(f"{medal} **{name}** — Level {u['level']} • {format_number(u['xp'])} XP")
            embed = base_embed(
                title=f"🏆 XP Leaderboard — {interaction.guild.name}",
                description="\n".join(lines),
                color=PURPLE,
                thumbnail=interaction.guild.icon.url if interaction.guild.icon else None,
            )
            embed.set_footer(text=f"Page {page_idx + 1}/{len(chunks)} • {BOT_NAME}")
            pages.append(embed)
        view = PaginatorView(pages, interaction.user)
        await interaction.response.send_message(embed=pages[0], view=view)


from config import BOT_NAME


async def setup(bot: commands.Bot):
    await bot.add_cog(Leveling(bot))
