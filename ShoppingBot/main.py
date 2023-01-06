import asyncio
import os

import discord
from discord.ext import commands

from Models.functions import settings_bot


intents = discord.Intents.all()
Bot = commands.Bot(command_prefix='>', intents = intents)
TOKEN = os.environ.get('TOKEN') or settings_bot["TOKEN"]



@Bot.event
async def on_ready():
    await Bot.change_presence(activity=discord.Game(name="Counter Strike 1.6"))
    print("i'm ready")


@Bot.event
async def on_command_error(ctx, error):
    print(error)
    print(type(error))
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Böyle bir komut yok!")
          

@Bot.command()
@commands.has_permissions(manage_roles=True) 
async def load(ctx, extension):
    """
    load cog 'extension'
    """
    await Bot.load_extension(f"cogs.{extension}")


@Bot.command()
@commands.has_permissions(manage_roles=True) 
async def unload(ctx, extension):
    """
    unload cog 'extension'
    """
    await Bot.unload_extension(f"cogs.{extension}")


@Bot.command()
@commands.has_permissions(manage_roles=True) 
async def reload(ctx, extension):
    """
    reload cog 'extension'
    """
    await Bot.unload_extension(f"cogs.{extension}")
    await Bot.load_extension(f"cogs.{extension}")




async def main():
    async with Bot:
        #Load cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await Bot.load_extension(f'cogs.{filename[:-3]}')

        await Bot.start(TOKEN)

asyncio.run(main())
