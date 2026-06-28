import discord
import platform
import asyncio
from datetime import datetime
from discord.ext import commands, tasks
from discord import app_commands
from utils.embeds import base_embed, success_embed, error_embed
from utils.helpers import format_time, parse_time, future_timestamp, timestamp_to_discord
from utils.paginator import PaginatorView, chunk_list
from database import get_db
from config import PINK, PURPLE, BOT_NAME, BOT_VERSION, SUPPORT_SERVER, INVITE_LINK, EMOJIS


class HelpSelect(discord.ui.Select):
    def __init__(self, categories: dict, bot: commands.Bot):
        self.categories = categories
        self.bot = bot
        options = [
            discord.SelectOption(label=k, emoji=v["emoji"], description=v["desc"])
            for k, v in categories.items()
        ]
        super().__init__(placeholder="🌸 Select a category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        cat = self.categories[self.values[0]]
        embed = base_embed(title=f"{cat['emoji']} {self.values[0]}", description="\n".join(cat["commands"]), color=PINK)
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, categories: dict, bot: commands.Bot, author: discord.User | discord.Member):
        super().__init__(timeout=120)
        self.author = author
        self.add_item(HelpSelect(categories, bot))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("This help menu isn't yours! 🌸", ephemeral=True)
            return False
        return True


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        self.reminder_task.start()

    def cog_unload(self):
        self.reminder_task.cancel()

    @tasks.loop(seconds=30)
    async def reminder_task(self):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with get_db() as conn:
            reminders = conn.execute(
                "SELECT * FROM reminders WHERE sent = 0 AND remind_at <= ?",
                (now,)
            ).fetchall()
        for r in reminders:
            channel = self.bot.get_channel(r["channel_id"])
            if channel:
                try:
                    embed = base_embed(title="⏰ Reminder!", description=r["message"], color=PINK)
                    await channel.send(f"<@{r['user_id']}>", embed=embed)
                except Exception:
                    pass
            with get_db() as conn:
                conn.execute("UPDATE reminders SET sent = 1 WHERE id = ?", (r["id"],))

    @reminder_task.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="ping", description="Check the bot's latency 🏓")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        color = 0x77DD77 if latency < 100 else 0xFFD700 if latency < 200 else 0xFF6B6B
        embed = base_embed(title="🏓 Pong!", description=f"**Latency:** `{latency}ms`", color=color)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show the help menu 🌸")
    async def help_cmd(self, interaction: discord.Interaction):
        categories = {
            "Welcome": {"emoji": "👋", "desc": "Welcome & goodbye system", "commands": [
                "`/welcome setup` — Configure welcome channel & message",
                "`/welcome disable` — Disable welcome messages",
                "`/welcome test` — Send a test welcome",
                "`/goodbye setup` — Configure goodbye channel",
                "`/goodbye disable` — Disable goodbye messages",
                "`/autorole add/remove/list` — Auto-role management",
                "`/boostmessage` — Configure boost announcements",
                "`/membercount` — View server member count",
            ]},
            "Moderation": {"emoji": "🛡️", "desc": "Server moderation tools", "commands": [
                "`/ban` — Ban a member", "`/unban` — Unban a user",
                "`/kick` — Kick a member", "`/mute/unmute` — Mute a member",
                "`/timeout/untimeout` — Timeout a member",
                "`/warn` — Warn a member", "`/warnings` — View warnings",
                "`/clear` — Clear messages", "`/slowmode` — Set slowmode",
                "`/lock/unlock` — Lock/unlock channels",
                "`/nickname` — Change nickname", "`/role` — Add/remove roles",
                "`/serverinfo` — Server info", "`/userinfo` — User info",
            ]},
            "Fun": {"emoji": "🎉", "desc": "Fun and games", "commands": [
                "`/8ball` — Ask the magic 8-ball", "`/coinflip` — Flip a coin",
                "`/dice` — Roll a dice", "`/rockpaperscissors` — Play RPS",
                "`/meme` — Random meme", "`/joke` — Random joke",
                "`/cat` — Random cat", "`/dog` — Random dog",
                "`/hug` — Hug someone", "`/slap` — Slap someone",
                "`/ship` — Ship two users", "`/rate` — Rate something",
                "`/avatar` — View avatar",
            ]},
            "Utility": {"emoji": "🔧", "desc": "Helpful utility commands", "commands": [
                "`/ping` — Check latency", "`/help` — This menu",
                "`/invite` — Invite the bot", "`/support` — Support server",
                "`/uptime` — Bot uptime", "`/botinfo` — Bot information",
                "`/remind` — Set a reminder", "`/poll` — Create a poll",
                "`/embed` — Create a custom embed", "`/calculate` — Calculate an expression",
                "`/timer` — Set a countdown timer",
            ]},
            "Economy": {"emoji": "💰", "desc": "Economy and currency", "commands": [
                "`/balance` — Check balance", "`/daily` — Claim daily reward",
                "`/work` — Earn coins", "`/beg` — Beg for coins",
                "`/deposit` — Deposit to bank", "`/withdraw` — Withdraw from bank",
                "`/pay` — Pay another user", "`/shop` — View the shop",
                "`/inventory` — View your inventory",
            ]},
            "Music": {"emoji": "🎵", "desc": "Music playback", "commands": [
                "`/play` — Play a song", "`/pause` — Pause music",
                "`/resume` — Resume music", "`/skip` — Skip current song",
                "`/stop` — Stop & disconnect", "`/queue` — View queue",
            ]},
            "Systems": {"emoji": "⚙️", "desc": "Server systems", "commands": [
                "`/ticket` — Open a support ticket", "`/giveaway start` — Start a giveaway",
                "`/suggest` — Submit a suggestion", "`/level` — Check your level",
                "`/leaderboard` — View XP leaderboard",
            ]},
        }
        embed = base_embed(
            title=f"🌸 {BOT_NAME} Help Menu",
            description="Select a category from the dropdown below to see its commands!\n\n💖 **Cute but powerful** — here to help your server thrive!",
            color=PINK,
        )
        embed.add_field(name="📊 Stats", value=f"**{len(self.bot.guilds):,}** servers\n**{sum(g.member_count for g in self.bot.guilds):,}** users", inline=True)
        embed.add_field(name="🔗 Links", value=f"[Invite]({INVITE_LINK}) | [Support]({SUPPORT_SERVER})", inline=True)
        view = HelpView(categories, self.bot, interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="invite", description="Get the bot's invite link 🔗")
    async def invite(self, interaction: discord.Interaction):
        embed = base_embed(title="🔗 Invite Alya", description=f"[Click here to invite me!]({INVITE_LINK})\n\n💖 Thank you for choosing Alya!", color=PINK)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="support", description="Join the support server 💬")
    async def support(self, interaction: discord.Interaction):
        embed = base_embed(title="💬 Support Server", description=f"[Join our support server!]({SUPPORT_SERVER})\n\n🌸 Get help, report bugs, and suggest features!", color=PINK)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="uptime", description="Check how long the bot has been running ⏱️")
    async def uptime(self, interaction: discord.Interaction):
        delta = datetime.utcnow() - self.start_time
        total_seconds = int(delta.total_seconds())
        embed = base_embed(title="⏱️ Uptime", description=f"I've been running for **{format_time(total_seconds)}**! 💪", color=PINK)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="botinfo", description="Information about the bot 🤖")
    async def botinfo(self, interaction: discord.Interaction):
        delta = datetime.utcnow() - self.start_time
        embed = base_embed(title=f"🌸 {BOT_NAME} Bot Info", color=PINK, thumbnail=self.bot.user.display_avatar.url)
        embed.add_field(name="Version", value=BOT_VERSION, inline=True)
        embed.add_field(name="Library", value=f"discord.py {discord.__version__}", inline=True)
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds):,}", inline=True)
        embed.add_field(name="Users", value=f"{sum(g.member_count for g in self.bot.guilds):,}", inline=True)
        embed.add_field(name="Uptime", value=format_time(int(delta.total_seconds())), inline=True)
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Commands", value=str(len(self.bot.tree.get_commands())), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remind", description="Set a reminder ⏰")
    @app_commands.describe(time="When to remind (e.g. 30m, 2h, 1d)", message="What to remind you about")
    async def remind(self, interaction: discord.Interaction, time: str, message: str):
        seconds = parse_time(time)
        if not seconds or seconds > 2592000:
            await interaction.response.send_message(embed=error_embed("Invalid Time", "Use format like `30m`, `2h`, `7d`. Max 30 days."), ephemeral=True)
            return
        remind_at = future_timestamp(seconds).strftime("%Y-%m-%d %H:%M:%S")
        with get_db() as conn:
            conn.execute(
                "INSERT INTO reminders (user_id, channel_id, message, remind_at) VALUES (?, ?, ?, ?)",
                (interaction.user.id, interaction.channel_id, message, remind_at)
            )
        embed = success_embed("Reminder Set!", f"I'll remind you in **{format_time(seconds)}**!\n> {message}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poll", description="Create a poll 📊")
    @app_commands.describe(question="Poll question", options="Options separated by | (up to 5)")
    async def poll(self, interaction: discord.Interaction, question: str, options: str = None):
        if options:
            opts = [o.strip() for o in options.split("|")][:5]
            if len(opts) < 2:
                await interaction.response.send_message(embed=error_embed("Too Few Options", "Provide at least 2 options separated by `|`."), ephemeral=True)
                return
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
            desc = "\n".join(f"{emojis[i]} {opt}" for i, opt in enumerate(opts))
            embed = base_embed(title=f"📊 {question}", description=desc, color=PURPLE)
            embed.set_footer(text=f"Poll by {interaction.user} • React to vote!")
            await interaction.response.send_message(embed=embed)
            msg = await interaction.original_response()
            for i in range(len(opts)):
                await msg.add_reaction(emojis[i])
        else:
            embed = base_embed(title=f"📊 {question}", description="Vote with 👍 or 👎!", color=PURPLE)
            embed.set_footer(text=f"Poll by {interaction.user}")
            await interaction.response.send_message(embed=embed)
            msg = await interaction.original_response()
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")

    @app_commands.command(name="embed", description="Create a custom embed ✨")
    @app_commands.describe(title="Embed title", description="Embed description", color="Hex color (e.g. ff69b4)")
    async def embed_cmd(self, interaction: discord.Interaction, title: str, description: str, color: str = "ff69b4"):
        try:
            clr = int(color.strip("#"), 16)
        except ValueError:
            clr = PINK
        embed = base_embed(title=title, description=description, color=clr)
        embed.set_footer(text=f"Created by {interaction.user}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="calculate", description="Calculate a math expression 🧮")
    @app_commands.describe(expression="Math expression to evaluate")
    async def calculate(self, interaction: discord.Interaction, expression: str):
        try:
            safe_expr = expression.replace("^", "**")
            allowed = set("0123456789+-*/().%** ")
            if not all(c in allowed for c in safe_expr):
                raise ValueError("Invalid characters")
            result = eval(safe_expr, {"__builtins__": {}}, {})
            embed = base_embed(title="🧮 Calculator", description=f"**Expression:** `{expression}`\n**Result:** `{result}`", color=PINK)
        except Exception:
            embed = error_embed("Calculation Error", f"Couldn't evaluate `{expression}`.\nUse simple math expressions only!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="timer", description="Set a countdown timer ⏱️")
    @app_commands.describe(duration="Duration (e.g. 1m, 30s)")
    async def timer(self, interaction: discord.Interaction, duration: str):
        seconds = parse_time(duration)
        if not seconds or seconds > 3600:
            await interaction.response.send_message(embed=error_embed("Invalid Duration", "Use format like `30s`, `5m`. Max 1 hour."), ephemeral=True)
            return
        embed = base_embed(title="⏱️ Timer Started!", description=f"Timer set for **{format_time(seconds)}**!\nI'll ping you when it's done. 🌸", color=PINK)
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(seconds)
        done_embed = base_embed(title="⏰ Timer Done!", description=f"{interaction.user.mention} Your **{format_time(seconds)}** timer is up! 🎉", color=PINK)
        await interaction.followup.send(embed=done_embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
