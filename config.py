import os
from typing import Final

BOT_TOKEN: Final = os.getenv("DISCORD_TOKEN", "")
BOT_PREFIX: Final = "!"
BOT_NAME: Final = "Alya"
BOT_VERSION: Final = "1.0.0"
OWNER_IDS: list[int] = [int(x) for x in os.getenv("OWNER_IDS", "0").split(",") if x.strip().isdigit()]

SUPPORT_SERVER: Final = os.getenv("SUPPORT_SERVER", "https://discord.gg/yourinvite")
INVITE_LINK: Final = os.getenv("INVITE_LINK", "https://discord.com/oauth2/authorize?client_id=1520801915959644181&permissions=8&integration_type=0&scope=bot+applications.commands")

PINK: Final = 0xFF69B4
PURPLE: Final = 0x9B59B6
LAVENDER: Final = 0xE6B0E6
ROSE: Final = 0xFF007F
SOFT_PINK: Final = 0xFFB6C1
SUCCESS_COLOR: Final = 0x77DD77
ERROR_COLOR: Final = 0xFF6B6B
WARNING_COLOR: Final = 0xFFD700
INFO_COLOR: Final = 0x87CEEB

DAILY_AMOUNT: Final = 500
WORK_MIN: Final = 100
WORK_MAX: Final = 400
BEG_MIN: Final = 10
BEG_MAX: Final = 100
XP_PER_MESSAGE: Final = 10
XP_COOLDOWN: Final = 60

STATUS_MESSAGES: Final = [
    ("watching", "🌸 Helping servers"),
    ("listening", "✨ /help"),
    ("playing", "💖 Making communities better"),
    ("playing", "🎵 Music & Fun"),
    ("watching", "🌙 Watching over the server"),
    ("playing", "🎀 Serving with love"),
    ("playing", "🍡 Anime vibes enabled"),
    ("playing", "⭐ Powered by Alya"),
    ("watching", "📚 Leveling and tickets"),
    ("playing", "💫 Cute but powerful"),
]

EMOJIS: Final = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "loading": "⏳",
    "star": "⭐",
    "heart": "💖",
    "flower": "🌸",
    "sparkles": "✨",
    "ribbon": "🎀",
    "music": "🎵",
    "coin": "🪙",
    "ticket": "🎫",
    "gift": "🎁",
    "level": "📊",
    "mod": "🛡️",
    "fun": "🎉",
    "utility": "🔧",
    "economy": "💰",
    "welcome": "👋",
    "crown": "👑",
    "ban": "🔨",
    "kick": "👢",
    "mute": "🔇",
    "warn": "⚠️",
    "lock": "🔒",
    "unlock": "🔓",
    "cat": "🐱",
    "dog": "🐶",
}

DATABASE_PATH: Final = "alya.db"

MEME_SUBREDDITS: Final = ["memes", "dankmemes", "meme", "AdviceAnimals", "me_irl"]
JOKE_API: Final = "https://v2.jokeapi.dev/joke/Any?safe-mode"
CAT_API: Final = "https://api.thecatapi.com/v1/images/search"
DOG_API: Final = "https://dog.ceo/api/breeds/image/random"
MEME_API: Final = "https://meme-api.com/gimme"

WORK_RESPONSES: Final = [
    "delivered pizzas 🍕",
    "walked dogs 🐕",
    "fixed computers 💻",
    "wrote code 👨‍💻",
    "cleaned houses 🏠",
    "tutored students 📚",
    "drove Uber 🚗",
    "sold lemonade 🍋",
    "streamed on Twitch 🎮",
    "drew anime art 🎨",
]

BEG_RESPONSES: Final = [
    "A kind stranger gave you some coins! 💝",
    "You found some coins on the ground! 🪙",
    "Someone took pity on you! 😢",
    "A rich person tossed you some change! 💸",
    "You performed on the street! 🎤",
]

SHIP_NAMES: Final = [
    "made in heaven", "star-crossed lovers", "eternal flames",
    "perfect match", "soul mates", "power couple",
    "cute couple", "unlikely duo", "chaotic pair",
]
