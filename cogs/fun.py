import discord
import random
import aiohttp
from discord.ext import commands
from discord import app_commands
from utils.embeds import base_embed, error_embed
from config import PINK, PURPLE, SOFT_PINK, EMOJIS, CAT_API, DOG_API, MEME_API, JOKE_API, SHIP_NAMES


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    async def _fetch_json(self, url: str) -> dict | list | None:
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            return None

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question 🎱")
    @app_commands.describe(question="Your question")
    async def eightball(self, interaction: discord.Interaction, question: str):
        responses = [
            ("✅ It is certain.", PINK),
            ("✅ It is decidedly so.", PINK),
            ("✅ Without a doubt.", PINK),
            ("✅ Yes — definitely.", PINK),
            ("✅ You may rely on it.", PINK),
            ("✅ As I see it, yes.", PINK),
            ("✅ Most likely.", PINK),
            ("✅ Outlook good.", PINK),
            ("✅ Yes!", PINK),
            ("✅ Signs point to yes.", PINK),
            ("🤷 Reply hazy, try again.", 0x808080),
            ("🤷 Ask again later.", 0x808080),
            ("🤷 Better not tell you now.", 0x808080),
            ("🤷 Cannot predict now.", 0x808080),
            ("🤷 Concentrate and ask again.", 0x808080),
            ("❌ Don't count on it.", PURPLE),
            ("❌ My reply is no.", PURPLE),
            ("❌ My sources say no.", PURPLE),
            ("❌ Outlook not so good.", PURPLE),
            ("❌ Very doubtful.", PURPLE),
        ]
        answer, color = random.choice(responses)
        embed = base_embed(title="🎱 Magic 8-Ball", description=f"**Question:** {question}\n\n**Answer:** {answer}", color=color)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin! 🪙")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        emoji = "🌕" if result == "Heads" else "🌑"
        embed = base_embed(title=f"🪙 Coin Flip — {result}!", description=f"{emoji} **{result}!**", color=PINK)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="dice", description="Roll a dice 🎲")
    @app_commands.describe(sides="Number of sides (default 6)")
    async def dice(self, interaction: discord.Interaction, sides: app_commands.Range[int, 2, 100] = 6):
        result = random.randint(1, sides)
        embed = base_embed(title="🎲 Dice Roll", description=f"You rolled a **d{sides}** and got **{result}**!", color=PINK)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rockpaperscissors", description="Play rock paper scissors! ✊✋✌️")
    @app_commands.describe(choice="Your choice")
    @app_commands.choices(choice=[
        app_commands.Choice(name="Rock ✊", value="rock"),
        app_commands.Choice(name="Paper ✋", value="paper"),
        app_commands.Choice(name="Scissors ✌️", value="scissors"),
    ])
    async def rps(self, interaction: discord.Interaction, choice: str):
        options = ["rock", "paper", "scissors"]
        emojis = {"rock": "✊", "paper": "✋", "scissors": "✌️"}
        bot_choice = random.choice(options)
        wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        if choice == bot_choice:
            result, color = "It's a tie! 🤝", 0x808080
        elif wins[choice] == bot_choice:
            result, color = "You win! 🎉", 0x77DD77
        else:
            result, color = "I win! 😈", PURPLE
        embed = base_embed(
            title="✊✋✌️ Rock Paper Scissors",
            description=f"You: **{emojis[choice]} {choice.title()}**\nMe: **{emojis[bot_choice]} {bot_choice.title()}**\n\n**{result}**",
            color=color
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="meme", description="Get a random meme 😂")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = await self._fetch_json(MEME_API)
        if data and "url" in data:
            embed = base_embed(title=f"😂 {data.get('title', 'Meme')}", color=PINK)
            embed.set_image(url=data["url"])
            embed.set_footer(text=f"👍 {data.get('ups', 0):,} | r/{data.get('subreddit', 'memes')}")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=error_embed("Meme Error", "Couldn't fetch a meme right now. Try again!"))

    @app_commands.command(name="joke", description="Get a random joke 😄")
    async def joke(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = await self._fetch_json(JOKE_API)
        if data:
            if data.get("type") == "single":
                desc = data["joke"]
            else:
                desc = f"{data['setup']}\n\n||{data['delivery']}||"
            embed = base_embed(title="😄 Random Joke", description=desc, color=SOFT_PINK)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=error_embed("Joke Error", "Couldn't fetch a joke right now!"))

    @app_commands.command(name="cat", description="Get a random cat photo 🐱")
    async def cat(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = await self._fetch_json(CAT_API)
        if data and len(data) > 0:
            embed = base_embed(title="🐱 Random Cat!", color=SOFT_PINK)
            embed.set_image(url=data[0]["url"])
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=error_embed("API Error", "Couldn't fetch a cat photo!"))

    @app_commands.command(name="dog", description="Get a random dog photo 🐶")
    async def dog(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = await self._fetch_json(DOG_API)
        if data and data.get("status") == "success":
            embed = base_embed(title="🐶 Random Dog!", color=SOFT_PINK)
            embed.set_image(url=data["message"])
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=error_embed("API Error", "Couldn't fetch a dog photo!"))

    @app_commands.command(name="hug", description="Hug someone! 🤗")
    @app_commands.describe(member="Who to hug")
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        embed = base_embed(
            title="🤗 Hug!",
            description=f"**{interaction.user.mention}** gave **{member.mention}** a big warm hug! 💖",
            color=SOFT_PINK
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="slap", description="Slap someone! 👋")
    @app_commands.describe(member="Who to slap")
    async def slap(self, interaction: discord.Interaction, member: discord.Member):
        embed = base_embed(
            title="👋 Slap!",
            description=f"**{interaction.user.mention}** slapped **{member.mention}**! Ouch! 😵",
            color=PURPLE
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ship", description="Ship two users together 💑")
    @app_commands.describe(user1="First user", user2="Second user")
    async def ship(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
        seed = user1.id + user2.id
        random.seed(seed)
        percentage = random.randint(0, 100)
        random.seed()
        bar_filled = int(percentage / 10)
        bar = "💗" * bar_filled + "🖤" * (10 - bar_filled)
        ship_name = random.choice(SHIP_NAMES)
        color = PINK if percentage >= 60 else PURPLE if percentage >= 30 else 0x808080
        embed = base_embed(
            title="💑 Ship Calculator",
            description=f"**{user1.display_name}** ❤️ **{user2.display_name}**\n\n{bar}\n\n**{percentage}% compatible** — *{ship_name}*",
            color=color
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rate", description="Rate something! ⭐")
    @app_commands.describe(thing="What to rate")
    async def rate(self, interaction: discord.Interaction, thing: str):
        random.seed(hash(thing))
        rating = random.randint(0, 100)
        random.seed()
        stars = "⭐" * (rating // 20)
        embed = base_embed(
            title="⭐ Rating",
            description=f"**{thing}**\n\n{stars or '💀'}\n\n**{rating}/100**",
            color=PINK
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Get a user's avatar 🖼️")
    @app_commands.describe(member="Member to get avatar of")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = base_embed(title=f"🖼️ {member.display_name}'s Avatar", color=PINK)
        embed.set_image(url=member.display_avatar.url)
        embed.add_field(name="Links", value=f"[PNG]({member.display_avatar.with_format('png').url}) | [JPG]({member.display_avatar.with_format('jpg').url}) | [WEBP]({member.display_avatar.with_format('webp').url})")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
