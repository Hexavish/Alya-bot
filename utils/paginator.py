import discord
from typing import Any


class PaginatorView(discord.ui.View):
    def __init__(self, pages: list[discord.Embed], author: discord.User | discord.Member, timeout: float = 120):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.author = author
        self.current = 0
        self._update_buttons()

    def _update_buttons(self):
        self.first_btn.disabled = self.current == 0
        self.prev_btn.disabled = self.current == 0
        self.next_btn.disabled = self.current == len(self.pages) - 1
        self.last_btn.disabled = self.current == len(self.pages) - 1
        self.page_btn.label = f"{self.current + 1}/{len(self.pages)}"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("This paginator isn't yours! 🌸", ephemeral=True)
            return False
        return True

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary, custom_id="first")
    async def first_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = 0
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.primary, custom_id="prev")
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(label="1/1", style=discord.ButtonStyle.secondary, custom_id="page", disabled=True)
    async def page_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.primary, custom_id="next")
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, custom_id="last")
    async def last_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = len(self.pages) - 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True


def chunk_list(lst: list[Any], size: int) -> list[list[Any]]:
    return [lst[i:i + size] for i in range(0, len(lst), size)]
