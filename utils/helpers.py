import re
import math
from datetime import datetime, timedelta
from config import EMOJIS


def format_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def format_time(seconds: int) -> str:
    intervals = [
        ("day", 86400),
        ("hour", 3600),
        ("minute", 60),
        ("second", 1),
    ]
    parts = []
    for name, count in intervals:
        if seconds >= count:
            value = seconds // count
            seconds %= count
            parts.append(f"{value} {name}{'s' if value != 1 else ''}")
    return ", ".join(parts) if parts else "0 seconds"


def parse_time(time_str: str) -> int | None:
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    match = re.fullmatch(r"(\d+)([smhdw])", time_str.lower().strip())
    if not match:
        return None
    amount, unit = int(match.group(1)), match.group(2)
    return amount * units[unit]


def xp_for_level(level: int) -> int:
    return math.floor(100 * (level ** 1.5))


def level_from_xp(xp: int) -> tuple[int, int, int]:
    level = 1
    while xp >= xp_for_level(level + 1):
        level += 1
    current_xp = xp - xp_for_level(level)
    next_xp = xp_for_level(level + 1) - xp_for_level(level)
    return level, current_xp, next_xp


def progress_bar(current: int, total: int, length: int = 10) -> str:
    filled = int((current / total) * length) if total > 0 else 0
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}]"


def timestamp_to_discord(dt: datetime, style: str = "R") -> str:
    ts = int(dt.timestamp())
    return f"<t:{ts}:{style}>"


def future_timestamp(seconds: int) -> datetime:
    return datetime.utcnow() + timedelta(seconds=seconds)


def truncate(text: str, length: int = 1024) -> str:
    if len(text) <= length:
        return text
    return text[:length - 3] + "..."


def clean_mentions(text: str) -> str:
    return re.sub(r"<@[!&]?\d+>|<#\d+>|<:\w+:\d+>|@everyone|@here", "[mention]", text)
