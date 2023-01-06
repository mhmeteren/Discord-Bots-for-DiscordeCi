import asyncio
import os

import discord
from discord.ext import commands

from models.functions import settings_bot
from Design.Auth import AuthModal


intents = discord.Intents.all()
Bot = commands.Bot(command_prefix='!', intents = intents)
Bot_TOKEN = os.environ.get('TOKEN') or settings_bot["TOKEN"]


@Bot.event
async def on_ready():
    await Bot.change_presence(activity=discord.Game(name="Counter strike 1.6"))
    print("i'm ready")


@Bot.event
async def on_command_error(ctx, error):
    print(error)
    print(type(error))
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Böyle bir komut yok!")


@Bot.command()
@commands.has_permissions(manage_roles=True) 
async def asd(ctx):
    if ctx.channel.name.endswith('authenticate'):
        async for message in ctx.channel.history(limit=None):
            await message.delete()

        view = discord.ui.View()
        btn = discord.ui.Button(label="Hesap dogrulama icin bana tıkla!", style=discord.ButtonStyle.green)
        view.add_item(btn)
        async def btn_callback(interaction: discord.Interaction):
            await interaction.response.send_modal(AuthModal())  
            
        btn.callback = btn_callback
        await ctx.send(view=view)

    else:
        await ctx.send("Bu kanal kullanılamaz sonu authenticate ile biten kanal seçin veya oluşturun", delete_after=5.0)



async def main():
    async with Bot:
        await Bot.start(Bot_TOKEN)

asyncio.run(main())
