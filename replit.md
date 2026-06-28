# Alya — Cute Anime Discord Bot

A full-featured, production-ready Discord bot with a cute anime-inspired pastel aesthetic. Powered by discord.py with slash commands, SQLite, and a cogs architecture.

## Run & Operate

- `python main.py` — Run the bot (via the "Alya Bot" workflow)
- Required secret: `DISCORD_TOKEN` — Your bot's token from the Discord Developer Portal
- Optional secrets: `OWNER_IDS` (comma-separated user IDs), `SUPPORT_SERVER`, `INVITE_LINK`

## Stack

- Python 3.11
- discord.py (latest, with voice support)
- SQLite via the `database.py` module (WAL mode, no ORM needed)
- Flask keep-alive server for Replit 24/7 hosting (port 8080)
- yt-dlp for music playback
- aiohttp for fun command APIs

## Where things live

- `main.py` — Bot entry point, cog loader, status rotation, global error handler
- `config.py` — All constants (colors, cooldowns, status messages, API URLs)
- `database.py` — SQLite helpers, schema init, all DB functions
- `keep_alive.py` — Flask thread for Replit UptimeRobot pinging
- `cogs/` — Feature cogs (welcome, moderation, fun, utility, economy, music, tickets, giveaway, suggestions, leveling, logging_cog)
- `utils/` — Shared utilities (embeds, checks, paginator, helpers)
- `alya.db` — SQLite database (auto-created on first run)
- `alya.log` — Log file (auto-created)

## Architecture decisions

- All embeds use pink/purple palette via helpers in `utils/embeds.py` — never build raw embeds in cogs
- Database uses context manager pattern via `get_db()` with WAL mode for concurrent access
- Economy cooldowns tracked in the `users` table as ISO timestamp strings (UTC)
- Ticket and giveaway views use `custom_id` persistence so they survive bot restarts
- Music queue is per-guild in-memory (lost on restart — by design for simplicity)

## Product

Alya is a public Discord bot with these systems:
- **Welcome/Goodbye/Auto-role** — automated member flow with configurable messages
- **Moderation** — ban, kick, mute, timeout, warn, clear, slowmode, lock, role management
- **Fun** — 8ball, coinflip, dice, RPS, memes, jokes, cat/dog, hug, slap, ship, rate, avatar
- **Utility** — ping, help menu with dropdown, reminders, polls, embeds, calculator, timer
- **Economy** — balance, daily, work, beg, deposit/withdraw, pay, shop, inventory
- **Music** — YouTube playback via yt-dlp with queue management
- **Tickets** — button-based ticket system with persistence across restarts
- **Giveaways** — timed giveaways with button entry and auto-end
- **Suggestions** — member suggestion submission with approve/deny workflow
- **Leveling** — XP on message with level-up announcements and paginated leaderboard
- **Logging** — bans, leaves, message deletes/edits, channel/role changes, voice updates
- **Status rotation** — 10 rotating cute statuses every 30 seconds

## User preferences

- Cute anime aesthetic, pink/purple colors
- Slash commands only (app_commands), no prefix commands exposed
- All embeds include footer "Alya • Cute but powerful 🌸"
- Professional production-ready structure

## Gotchas

- Music requires ffmpeg to be installed for audio processing (`installSystemDependencies(["ffmpeg"])`)
- Slash commands take up to 1 hour to appear globally after first sync (normal Discord behavior)
- The keep-alive server runs on port 8080 — use UptimeRobot to ping it for 24/7 hosting
- `OWNER_IDS` env var should be comma-separated Discord user IDs for owner-only commands
- Do NOT commit `alya.db` or `alya.log` to version control

## Pointers

- See the `pnpm-workspace` skill for workspace structure details
- Discord Developer Portal: https://discord.com/developers/applications
