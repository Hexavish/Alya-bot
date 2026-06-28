import discord
from discord.ext import commands
from discord import app_commands
from database import get_guild, update_guild, ensure_guild, get_db
from utils.embeds import base_embed, success_embed, error_embed
from utils.checks import has_manage_guild
from config import PINK, PURPLE, EMOJIS


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        with get_db() as conn:
            ticket = conn.execute("SELECT * FROM tickets WHERE channel_id = ? AND status = 'open'", (channel.id,)).fetchone()
        if not ticket:
            await interaction.response.send_message("This isn't an active ticket!", ephemeral=True)
            return
        can_close = (
            interaction.user.id == ticket["user_id"] or
            interaction.user.guild_permissions.manage_channels
        )
        if not can_close:
            await interaction.response.send_message("You don't have permission to close this ticket!", ephemeral=True)
            return
        with get_db() as conn:
            conn.execute("UPDATE tickets SET status = 'closed' WHERE channel_id = ?", (channel.id,))
        await interaction.response.send_message(embed=base_embed(title="🔒 Ticket Closing", description="This ticket will be deleted in 5 seconds...", color=PURPLE))
        import asyncio
        await asyncio.sleep(5)
        await channel.delete(reason=f"Ticket closed by {interaction.user}")


class TicketCreateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", emoji="🎫", style=discord.ButtonStyle.primary, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        guild_data = get_guild(guild.id)
        if not guild_data:
            await interaction.response.send_message("Ticket system not configured!", ephemeral=True)
            return

        with get_db() as conn:
            existing = conn.execute(
                "SELECT channel_id FROM tickets WHERE user_id = ? AND guild_id = ? AND status = 'open'",
                (interaction.user.id, guild.id)
            ).fetchone()

        if existing:
            ch = guild.get_channel(existing["channel_id"])
            if ch:
                await interaction.response.send_message(f"You already have an open ticket: {ch.mention}", ephemeral=True)
                return

        category_id = guild_data.get("ticket_category")
        category = guild.get_channel(category_id) if category_id else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        }

        support_role_id = guild_data.get("ticket_support_role")
        if support_role_id:
            support_role = guild.get_role(support_role_id)
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        with get_db() as conn:
            count = conn.execute("SELECT COUNT(*) as c FROM tickets WHERE guild_id = ?", (guild.id,)).fetchone()["c"] + 1

        channel = await guild.create_text_channel(
            name=f"ticket-{count:04d}",
            category=category,
            overwrites=overwrites,
            topic=f"Ticket by {interaction.user} ({interaction.user.id})"
        )

        with get_db() as conn:
            conn.execute(
                "INSERT INTO tickets (guild_id, channel_id, user_id) VALUES (?, ?, ?)",
                (guild.id, channel.id, interaction.user.id)
            )

        embed = base_embed(
            title=f"{EMOJIS['ticket']} Ticket #{count:04d}",
            description=f"Welcome {interaction.user.mention}!\nOur support team will be with you shortly. 💖\n\nDescribe your issue below.",
            color=PINK,
        )
        view = TicketCloseView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Your ticket has been created: {channel.mention} 🎫", ephemeral=True)


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(TicketCreateView())
        bot.add_view(TicketCloseView())

    ticket_group = app_commands.Group(name="ticket", description="Ticket system")

    @ticket_group.command(name="setup", description="Set up the ticket system")
    @has_manage_guild()
    @app_commands.describe(channel="Channel where the ticket panel will be posted", category="Category for ticket channels", support_role="Role that can see tickets")
    async def ticket_setup(self, interaction: discord.Interaction, channel: discord.TextChannel, category: discord.CategoryChannel = None, support_role: discord.Role = None):
        ensure_guild(interaction.guild_id)
        update_guild(
            interaction.guild_id,
            ticket_category=category.id if category else None,
            ticket_support_role=support_role.id if support_role else None
        )
        embed = base_embed(
            title=f"{EMOJIS['ticket']} Support Tickets",
            description="🌸 Click the button below to open a support ticket!\n\nOur team is here to help you. 💖",
            color=PINK,
        )
        view = TicketCreateView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(embed=success_embed("Ticket System Set Up!", f"Ticket panel posted in {channel.mention}!"))

    @ticket_group.command(name="close", description="Close the current ticket")
    async def ticket_close(self, interaction: discord.Interaction):
        with get_db() as conn:
            ticket = conn.execute("SELECT * FROM tickets WHERE channel_id = ? AND status = 'open'", (interaction.channel_id,)).fetchone()
        if not ticket:
            await interaction.response.send_message(embed=error_embed("Not a Ticket", "This command can only be used in an open ticket channel."), ephemeral=True)
            return
        view = TicketCloseView()
        await interaction.response.send_message(embed=base_embed(title="Close Ticket?", description="Are you sure you want to close this ticket?", color=PURPLE), view=view)

    @ticket_group.command(name="list", description="List all open tickets")
    @has_manage_guild()
    async def ticket_list(self, interaction: discord.Interaction):
        with get_db() as conn:
            tickets = conn.execute(
                "SELECT * FROM tickets WHERE guild_id = ? AND status = 'open' ORDER BY created_at DESC LIMIT 20",
                (interaction.guild_id,)
            ).fetchall()
        if not tickets:
            await interaction.response.send_message(embed=success_embed("No Open Tickets", "There are no open tickets right now! 🌸"))
            return
        desc = "\n".join(f"**#{t['id']:04d}** — <@{t['user_id']}> — <#{t['channel_id']}>" for t in tickets)
        embed = base_embed(title=f"{EMOJIS['ticket']} Open Tickets ({len(tickets)})", description=desc, color=PINK)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
