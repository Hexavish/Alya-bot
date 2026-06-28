import discord
import asyncio
import logging
import os
import sys
from discord.ext import commands, tasks
from dotenv import load_dotenv
from database import init_db
from keep_alive import keep_alive
from config import BOT_TOKEN, STATUS_MESSAGES, BOT_NAME

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("alya.log", encoding="utf-8"),
    ],
)
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord.http").setLevel(logging.WARNING)
logger = logging.getLogger(BOT_NAME)

COGS = [
    "cogs.welcome",
    "cogs.moderation",
    "cogs.fun",
    "cogs.utility",
    "cogs.economy",
    "cogs.music",
    "cogs.tickets",
    "cogs.giveaway",
    "cogs.suggestions",
    "cogs.leveling",
    "cogs.logging_cog",
]


class Alya(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None,
            case_insensitive=True,
        )
        self._status_index = 0

    async def setup_hook(self):
        logger.info(f"Setting up {BOT_NAME}...")
        for cog in COGS:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")

        logger.info("Syncing slash commands...")
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} global command(s).")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_ready(self):
        logger.info("=" * 40)
        logger.info(f"  {BOT_NAME} is online!")
        logger.info(f"  User: {self.user} (ID: {self.user.id})")
        logger.info(f"  Guilds: {len(self.guilds)}")
        logger.info(f"  Users: {sum(g.member_count for g in self.guilds):,}")
        logger.info("=" * 40)
        self.status_rotation.start()

    async def on_guild_join(self, guild: discord.Guild):
        from database import ensure_guild
        ensure_guild(guild.id)
        logger.info(f"Joined guild: {guild.name} ({guild.id})")

    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        from utils.embeds import error_embed
        if isinstance(error, discord.app_commands.CheckFailure):
            await self._safe_respond(interaction, error_embed("Permission Denied", str(error)))
        elif isinstance(error, discord.app_commands.CommandOnCooldown):
            await self._safe_respond(interaction, error_embed("Cooldown", f"Try again in `{error.retry_after:.1f}s`. ⏳"))
        elif isinstance(error, discord.app_commands.MissingPermissions):
            await self._safe_respond(interaction, error_embed("Missing Permissions", "You don't have permission for this!"))
        else:
            logger.error(f"Command error in /{interaction.command.name if interaction.command else 'unknown'}: {error}")
            await self._safe_respond(interaction, error_embed("An Error Occurred", f"Something went wrong! Please try again.\n`{type(error).__name__}`"))

    async def _safe_respond(self, interaction: discord.Interaction, embed: discord.Embed):
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            pass

    @tasks.loop(seconds=30)
    async def status_rotation(self):
        kind, text = STATUS_MESSAGES[self._status_index % len(STATUS_MESSAGES)]
        if kind == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=text)
        elif kind == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=text)
        else:
            activity = discord.Game(name=text)
        await self.change_presence(status=discord.Status.online, activity=activity)
        self._status_index += 1

    @status_rotation.before_loop
    async def before_status(self):
        await self.wait_until_ready()


async def main():
    token = BOT_TOKEN or os.getenv("DISCORD_TOKEN", "")
    if not token:
        logger.critical("DISCORD_TOKEN is not set! Set it in your Replit Secrets.")
        sys.exit(1)

    init_db()
    logger.info("Database initialized.")

    keep_alive()
    logger.info("Keep-alive server started on port 8080.")

    bot = Alya()
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
