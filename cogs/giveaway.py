import discord
import random
import json
import asyncio
from datetime import datetime
from discord.ext import commands, tasks
from discord import app_commands
from database import get_db
from utils.embeds import base_embed, success_embed, error_embed
from utils.helpers import parse_time, format_time, future_timestamp
from utils.checks import has_manage_guild
from config import PINK, PURPLE, EMOJIS


class GiveawayEnterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Enter Giveaway", emoji="🎁", style=discord.ButtonStyle.success, custom_id="giveaway_enter")
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        with get_db() as conn:
            giveaway = conn.execute(
                "SELECT * FROM giveaways WHERE message_id = ? AND ended = 0",
                (interaction.message.id,)
            ).fetchone()
        if not giveaway:
            await interaction.response.send_message("This giveaway has ended!", ephemeral=True)
            return
        entries = json.loads(giveaway["entries"])
        if interaction.user.id in entries:
            entries.remove(interaction.user.id)
            with get_db() as conn:
                conn.execute("UPDATE giveaways SET entries = ? WHERE message_id = ?", (json.dumps(entries), interaction.message.id))
            await interaction.response.send_message("You've left the giveaway! 👋", ephemeral=True)
        else:
            entries.append(interaction.user.id)
            with get_db() as conn:
                conn.execute("UPDATE giveaways SET entries = ? WHERE message_id = ?", (json.dumps(entries), interaction.message.id))
            await interaction.response.send_message(f"You've entered! 🎁 **{len(entries)}** entries so far.", ephemeral=True)


class Giveaway(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(GiveawayEnterView())
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with get_db() as conn:
            giveaways = conn.execute(
                "SELECT * FROM giveaways WHERE ended = 0 AND ends_at <= ?",
                (now,)
            ).fetchall()
        for g in giveaways:
            await self.end_giveaway(g)

    @check_giveaways.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    async def end_giveaway(self, giveaway):
        with get_db() as conn:
            conn.execute("UPDATE giveaways SET ended = 1 WHERE id = ?", (giveaway["id"],))
        channel = self.bot.get_channel(giveaway["channel_id"])
        if not channel:
            return
        entries = json.loads(giveaway["entries"])
        winners_count = min(giveaway["winners"], len(entries))
        if entries and winners_count > 0:
            winners = random.sample(entries, winners_count)
            winner_mentions = " ".join(f"<@{w}>" for w in winners)
            await channel.send(
                embed=base_embed(
                    title="🎉 Giveaway Ended!",
                    description=f"**Prize:** {giveaway['prize']}\n**Winner(s):** {winner_mentions}\n\nCongratulations! 🎊",
                    color=PINK
                )
            )
        else:
            await channel.send(embed=base_embed(title="😢 Giveaway Ended", description=f"**Prize:** {giveaway['prize']}\n\nNo valid entries! No winner selected.", color=PURPLE))
        try:
            msg = await channel.fetch_message(giveaway["message_id"])
            ended_embed = base_embed(title="🎁 Giveaway (Ended)", description=f"**Prize:** {giveaway['prize']}\n**Winners:** {giveaway['winners']}\n**Host:** <@{giveaway['host_id']}>\n\nThis giveaway has ended!", color=PURPLE)
            await msg.edit(embed=ended_embed, view=None)
        except Exception:
            pass

    giveaway_group = app_commands.Group(name="giveaway", description="Giveaway system")

    @giveaway_group.command(name="start", description="Start a giveaway 🎁")
    @has_manage_guild()
    @app_commands.describe(duration="Duration (e.g. 1h, 1d)", winners="Number of winners", prize="What to give away", channel="Channel for giveaway")
    async def giveaway_start(self, interaction: discord.Interaction, duration: str, winners: app_commands.Range[int, 1, 20], prize: str, channel: discord.TextChannel = None):
        seconds = parse_time(duration)
        if not seconds:
            await interaction.response.send_message(embed=error_embed("Invalid Duration", "Use format like `1h`, `2d`."), ephemeral=True)
            return
        ch = channel or interaction.channel
        ends_at = future_timestamp(seconds)
        ends_at_str = ends_at.strftime("%Y-%m-%d %H:%M:%S")
        embed = base_embed(
            title="🎁 Giveaway!",
            description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Host:** {interaction.user.mention}\n**Ends:** <t:{int(ends_at.timestamp())}:R>\n\nClick the button to enter! 🌸",
            color=PINK,
        )
        view = GiveawayEnterView()
        await interaction.response.send_message(embed=success_embed("Giveaway Started!", f"Giveaway posted in {ch.mention}!"), ephemeral=True)
        msg = await ch.send(embed=embed, view=view)
        with get_db() as conn:
            conn.execute(
                "INSERT INTO giveaways (guild_id, channel_id, message_id, host_id, prize, winners, ends_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (interaction.guild_id, ch.id, msg.id, interaction.user.id, prize, winners, ends_at_str)
            )

    @giveaway_group.command(name="end", description="End a giveaway early")
    @has_manage_guild()
    @app_commands.describe(message_id="Message ID of the giveaway")
    async def giveaway_end(self, interaction: discord.Interaction, message_id: str):
        with get_db() as conn:
            g = conn.execute("SELECT * FROM giveaways WHERE message_id = ? AND ended = 0", (int(message_id),)).fetchone()
        if not g:
            await interaction.response.send_message(embed=error_embed("Not Found", "Couldn't find an active giveaway with that message ID."), ephemeral=True)
            return
        await interaction.response.send_message(embed=success_embed("Ending Giveaway", "Ending the giveaway now..."), ephemeral=True)
        await self.end_giveaway(g)

    @giveaway_group.command(name="reroll", description="Reroll a giveaway winner")
    @has_manage_guild()
    @app_commands.describe(message_id="Message ID of the ended giveaway")
    async def giveaway_reroll(self, interaction: discord.Interaction, message_id: str):
        with get_db() as conn:
            g = conn.execute("SELECT * FROM giveaways WHERE message_id = ? AND ended = 1", (int(message_id),)).fetchone()
        if not g:
            await interaction.response.send_message(embed=error_embed("Not Found", "Couldn't find an ended giveaway with that ID."), ephemeral=True)
            return
        entries = json.loads(g["entries"])
        if not entries:
            await interaction.response.send_message(embed=error_embed("No Entries", "No entries to reroll!"), ephemeral=True)
            return
        winner = random.choice(entries)
        await interaction.response.send_message(embed=base_embed(title="🎲 Giveaway Reroll!", description=f"New winner: <@{winner}> — **{g['prize']}**!", color=PINK))


async def setup(bot: commands.Bot):
    await bot.add_cog(Giveaway(bot))
