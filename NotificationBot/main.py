import asyncio
import os

import discord
from discord.ext import commands, tasks

from Models.functions import settings_bot

from Design.productView import ProductViewer

intents = discord.Intents.all()
Bot = commands.Bot(command_prefix='|', intents = intents)
TOKEN = os.environ.get('TOKEN') or settings_bot["TOKEN"]



@Bot.event
async def on_ready():
    global categoryCahannel
    global brandCahannel
    categoryCahannel = getChannel(settings_bot["categoryCahannel"])
    brandCahannel = getChannel(settings_bot["brandCahannel"])
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
async def clear(ctx: commands.context.Context, amount: int):
    await ctx.channel.purge(limit=amount)


@Bot.command()
@commands.has_permissions(manage_roles=True) 
async def pnoti(ctx: commands.context.Context):
    if ProductsList.is_running():
        ProductsList.stop()
    else:
        ProductsList.start()


@tasks.loop(seconds=10)
async def ProductsList():
    if categoryCahannel:
        sp = ProductViewer()
        await sp.getProduct(Txtchannel=categoryCahannel, page=1, page_size=3, Bot=Bot)



def getChannel(_name):
    for c in Bot.get_all_channels():
        if c.name == _name:
            return c
    return None


async def main():
    async with Bot:
        await Bot.start(TOKEN)

asyncio.run(main())


