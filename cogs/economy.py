import discord
import random
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands
from database import get_user, update_user, ensure_user, get_db, get_leaderboard
from utils.embeds import base_embed, success_embed, error_embed
from utils.helpers import format_number
from config import PINK, PURPLE, DAILY_AMOUNT, WORK_MIN, WORK_MAX, BEG_MIN, BEG_MAX, WORK_RESPONSES, BEG_RESPONSES, EMOJIS


def on_cooldown(last_time_str: str, cooldown_seconds: int) -> tuple[bool, int]:
    if not last_time_str:
        return False, 0
    last = datetime.fromisoformat(last_time_str)
    elapsed = (datetime.utcnow() - last).total_seconds()
    remaining = cooldown_seconds - elapsed
    return remaining > 0, max(0, int(remaining))


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="balance", description="Check your balance 💰")
    @app_commands.describe(member="Check another user's balance")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        user = get_user(target.id, interaction.guild_id)
        embed = base_embed(
            title=f"{EMOJIS['coin']} {target.display_name}'s Balance",
            color=PINK,
            thumbnail=target.display_avatar.url,
        )
        embed.add_field(name="💵 Wallet", value=f"**{format_number(user['balance'])}** coins", inline=True)
        embed.add_field(name="🏦 Bank", value=f"**{format_number(user['bank'])}** coins", inline=True)
        embed.add_field(name="💎 Net Worth", value=f"**{format_number(user['balance'] + user['bank'])}** coins", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="daily", description="Claim your daily reward 🎁")
    async def daily(self, interaction: discord.Interaction):
        user = get_user(interaction.user.id, interaction.guild_id)
        cd, remaining = on_cooldown(user["last_daily"], 86400)
        if cd:
            hours, rem = divmod(remaining, 3600)
            minutes = rem // 60
            await interaction.response.send_message(
                embed=error_embed("Cooldown", f"Come back in **{hours}h {minutes}m**! ⏳"),
                ephemeral=True
            )
            return
        amount = DAILY_AMOUNT + random.randint(0, 200)
        new_balance = user["balance"] + amount
        update_user(interaction.user.id, interaction.guild_id,
                    balance=new_balance, last_daily=datetime.utcnow().isoformat())
        embed = success_embed(f"Daily Claimed! {EMOJIS['gift']}", f"You received **{format_number(amount)}** coins!\n💰 Balance: **{format_number(new_balance)}**")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Work to earn coins 💼")
    async def work(self, interaction: discord.Interaction):
        user = get_user(interaction.user.id, interaction.guild_id)
        cd, remaining = on_cooldown(user["last_work"], 3600)
        if cd:
            minutes = remaining // 60
            await interaction.response.send_message(
                embed=error_embed("Cooldown", f"You're tired! Rest for **{minutes}** more minutes. ⏳"),
                ephemeral=True
            )
            return
        job = random.choice(WORK_RESPONSES)
        amount = random.randint(WORK_MIN, WORK_MAX)
        new_balance = user["balance"] + amount
        update_user(interaction.user.id, interaction.guild_id,
                    balance=new_balance, last_work=datetime.utcnow().isoformat())
        embed = success_embed("Work Complete! 💼", f"You {job} and earned **{format_number(amount)}** coins!\n💰 Balance: **{format_number(new_balance)}**")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="beg", description="Beg for some coins 🙏")
    async def beg(self, interaction: discord.Interaction):
        user = get_user(interaction.user.id, interaction.guild_id)
        cd, remaining = on_cooldown(user["last_beg"], 300)
        if cd:
            await interaction.response.send_message(
                embed=error_embed("Cooldown", f"Wait **{remaining}** more seconds before begging again! ⏳"),
                ephemeral=True
            )
            return
        if random.random() < 0.2:
            update_user(interaction.user.id, interaction.guild_id, last_beg=datetime.utcnow().isoformat())
            await interaction.response.send_message(embed=error_embed("Rejected! 😢", "Nobody gave you anything this time..."))
            return
        amount = random.randint(BEG_MIN, BEG_MAX)
        new_balance = user["balance"] + amount
        response = random.choice(BEG_RESPONSES)
        update_user(interaction.user.id, interaction.guild_id,
                    balance=new_balance, last_beg=datetime.utcnow().isoformat())
        embed = success_embed("Received! 🙏", f"{response}\nYou got **{format_number(amount)}** coins!\n💰 Balance: **{format_number(new_balance)}**")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deposit", description="Deposit coins to your bank 🏦")
    @app_commands.describe(amount="Amount to deposit (or 'all')")
    async def deposit(self, interaction: discord.Interaction, amount: str):
        user = get_user(interaction.user.id, interaction.guild_id)
        if amount.lower() == "all":
            dep = user["balance"]
        else:
            try:
                dep = int(amount)
            except ValueError:
                await interaction.response.send_message(embed=error_embed("Invalid Amount", "Enter a number or 'all'."), ephemeral=True)
                return
        if dep <= 0 or dep > user["balance"]:
            await interaction.response.send_message(embed=error_embed("Invalid Amount", f"You only have **{format_number(user['balance'])}** coins in your wallet."), ephemeral=True)
            return
        update_user(interaction.user.id, interaction.guild_id,
                    balance=user["balance"] - dep, bank=user["bank"] + dep)
        await interaction.response.send_message(embed=success_embed("Deposited! 🏦", f"Deposited **{format_number(dep)}** coins to your bank.\n🏦 Bank: **{format_number(user['bank'] + dep)}**"))

    @app_commands.command(name="withdraw", description="Withdraw coins from your bank 💵")
    @app_commands.describe(amount="Amount to withdraw (or 'all')")
    async def withdraw(self, interaction: discord.Interaction, amount: str):
        user = get_user(interaction.user.id, interaction.guild_id)
        if amount.lower() == "all":
            wd = user["bank"]
        else:
            try:
                wd = int(amount)
            except ValueError:
                await interaction.response.send_message(embed=error_embed("Invalid Amount", "Enter a number or 'all'."), ephemeral=True)
                return
        if wd <= 0 or wd > user["bank"]:
            await interaction.response.send_message(embed=error_embed("Invalid Amount", f"You only have **{format_number(user['bank'])}** coins in your bank."), ephemeral=True)
            return
        update_user(interaction.user.id, interaction.guild_id,
                    balance=user["balance"] + wd, bank=user["bank"] - wd)
        await interaction.response.send_message(embed=success_embed("Withdrawn! 💵", f"Withdrew **{format_number(wd)}** coins from your bank.\n💵 Wallet: **{format_number(user['balance'] + wd)}**"))

    @app_commands.command(name="pay", description="Pay another user coins 💸")
    @app_commands.describe(member="Who to pay", amount="Amount to pay")
    async def pay(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if member.id == interaction.user.id:
            await interaction.response.send_message(embed=error_embed("Invalid", "You can't pay yourself!"), ephemeral=True)
            return
        if amount <= 0:
            await interaction.response.send_message(embed=error_embed("Invalid Amount", "Amount must be positive!"), ephemeral=True)
            return
        user = get_user(interaction.user.id, interaction.guild_id)
        if user["balance"] < amount:
            await interaction.response.send_message(embed=error_embed("Insufficient Funds", f"You only have **{format_number(user['balance'])}** coins!"), ephemeral=True)
            return
        target = get_user(member.id, interaction.guild_id)
        update_user(interaction.user.id, interaction.guild_id, balance=user["balance"] - amount)
        update_user(member.id, interaction.guild_id, balance=target["balance"] + amount)
        await interaction.response.send_message(embed=success_embed("Payment Sent! 💸", f"You paid **{format_number(amount)}** coins to {member.mention}!"))

    @app_commands.command(name="shop", description="View the server shop 🏪")
    async def shop(self, interaction: discord.Interaction):
        with get_db() as conn:
            items = conn.execute("SELECT * FROM shop_items WHERE guild_id = ?", (interaction.guild_id,)).fetchall()
        if not items:
            await interaction.response.send_message(embed=base_embed(title="🏪 Shop", description="The shop is empty! Server admins can add items. 🛒", color=PINK))
            return
        desc = "\n".join(f"**{i['name']}** — {format_number(i['price'])} coins\n> {i['description'] or 'No description'}" for i in items)
        embed = base_embed(title="🏪 Server Shop", description=desc, color=PINK)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="inventory", description="View your inventory 🎒")
    async def inventory(self, interaction: discord.Interaction):
        with get_db() as conn:
            items = conn.execute(
                "SELECT * FROM inventory WHERE user_id = ? AND guild_id = ?",
                (interaction.user.id, interaction.guild_id)
            ).fetchall()
        if not items:
            await interaction.response.send_message(embed=base_embed(title="🎒 Inventory", description="Your inventory is empty! Visit the `/shop`. 🛒", color=PINK))
            return
        desc = "\n".join(f"**{i['item_name']}** × {i['quantity']}" for i in items)
        embed = base_embed(title=f"🎒 {interaction.user.display_name}'s Inventory", description=desc, color=PINK)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
