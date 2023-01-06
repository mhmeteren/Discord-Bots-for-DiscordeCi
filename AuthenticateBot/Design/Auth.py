import discord
from discord.ui import Modal, TextInput

from models.model import DiscordAcc
from models.functions import settings_bot

class AuthModal(Modal, title="Activate Account"):
    TOKEN = TextInput(label="Enter your activate token", placeholder="abc123...", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Integration):
        user = DiscordAcc(interaction.user.id)
        status =  user.DiscordAccControl(self.TOKEN)
        await interaction.guild.get_channel(settings_bot["userlogs"]).send(f'<@{interaction.user.id}>, Authentication Status: {status}', ephemeral=True)
        await interaction.response.defer(ephemeral=False, thinking=False)

    
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.guild.get_channel(settings_bot["userErorlogs"]).send(f'<@{interaction.user.id}>, Error: {str(error)}')
    
