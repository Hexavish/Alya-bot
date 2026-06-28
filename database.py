import sqlite3
import logging
from contextlib import contextmanager
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS guilds (
                guild_id INTEGER PRIMARY KEY,
                welcome_channel INTEGER,
                goodbye_channel INTEGER,
                welcome_message TEXT,
                goodbye_message TEXT,
                welcome_enabled INTEGER DEFAULT 0,
                goodbye_enabled INTEGER DEFAULT 0,
                log_channel INTEGER,
                suggestion_channel INTEGER,
                ticket_category INTEGER,
                ticket_log INTEGER,
                ticket_support_role INTEGER,
                boost_channel INTEGER,
                boost_message TEXT
            );

            CREATE TABLE IF NOT EXISTS autoroles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                UNIQUE(guild_id, role_id)
            );

            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                balance INTEGER DEFAULT 0,
                bank INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_daily TEXT,
                last_work TEXT,
                last_beg TEXT,
                last_xp TEXT,
                warnings INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, guild_id)
            );

            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                timestamp TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS mutes (
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                expires_at TEXT,
                PRIMARY KEY (user_id, guild_id)
            );

            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'open',
                created_at TEXT DEFAULT (datetime('now')),
                subject TEXT
            );

            CREATE TABLE IF NOT EXISTS giveaways (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                message_id INTEGER,
                host_id INTEGER NOT NULL,
                prize TEXT NOT NULL,
                winners INTEGER DEFAULT 1,
                ends_at TEXT NOT NULL,
                ended INTEGER DEFAULT 0,
                entries TEXT DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                suggestion TEXT NOT NULL,
                message_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                sent INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL,
                role_id INTEGER,
                quantity INTEGER DEFAULT -1
            );

            CREATE INDEX IF NOT EXISTS idx_users_guild ON users(guild_id);
            CREATE INDEX IF NOT EXISTS idx_warnings_user ON warnings(user_id, guild_id);
            CREATE INDEX IF NOT EXISTS idx_tickets_guild ON tickets(guild_id);
            CREATE INDEX IF NOT EXISTS idx_giveaways_guild ON giveaways(guild_id);
        """)
    logger.info("Database initialized successfully.")


def get_guild(guild_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM guilds WHERE guild_id = ?", (guild_id,)).fetchone()
        return dict(row) if row else None


def ensure_guild(guild_id: int):
    with get_db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO guilds (guild_id) VALUES (?)",
            (guild_id,)
        )


def ensure_user(user_id: int, guild_id: int):
    with get_db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, guild_id) VALUES (?, ?)",
            (user_id, guild_id)
        )


def get_user(user_id: int, guild_id: int) -> dict | None:
    ensure_user(user_id, guild_id)
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id)
        ).fetchone()
        return dict(row) if row else None


def update_user(user_id: int, guild_id: int, **kwargs):
    ensure_user(user_id, guild_id)
    if not kwargs:
        return
    cols = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id, guild_id]
    with get_db() as conn:
        conn.execute(
            f"UPDATE users SET {cols} WHERE user_id = ? AND guild_id = ?",
            vals
        )


def update_guild(guild_id: int, **kwargs):
    ensure_guild(guild_id)
    if not kwargs:
        return
    cols = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [guild_id]
    with get_db() as conn:
        conn.execute(
            f"UPDATE guilds SET {cols} WHERE guild_id = ?",
            vals
        )


def add_warning(user_id: int, guild_id: int, moderator_id: int, reason: str) -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO warnings (user_id, guild_id, moderator_id, reason) VALUES (?, ?, ?, ?)",
            (user_id, guild_id, moderator_id, reason)
        )
        conn.execute(
            "UPDATE users SET warnings = warnings + 1 WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id)
        )
        return cur.lastrowid


def get_warnings(user_id: int, guild_id: int) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM warnings WHERE user_id = ? AND guild_id = ? ORDER BY timestamp DESC",
            (user_id, guild_id)
        ).fetchall()
        return [dict(r) for r in rows]


def get_leaderboard(guild_id: int, limit: int = 10) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM users WHERE guild_id = ? ORDER BY xp DESC LIMIT ?",
            (guild_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]
