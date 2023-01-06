import asyncio
import json
import time
import os

import discord
from discord.ext import commands

from models.functions import settings_bot

intents = discord.Intents.all()
Bot = commands.Bot(command_prefix='!', intents = intents)
TOKEN = os.environ.get('TOKEN') or settings_bot["TOKEN"]

RolesEmoji = []
delay = 5


@Bot.event
async def on_ready():
    await Bot.change_presence(activity=discord.Game(name="Counter strike 1.6"))
    print("i'm ready")




@Bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Böyle bir komut yok!")



@Bot.command()
@commands.has_permissions(manage_roles=True) 
async def setupServer(ctx):
    await ctx.send(f"Merhaba! {delay} saniye içinde işlem başlatılıcaktır...")
    await ctx.send("setup-satatus-channel kanalından işlemleri görebilirsiniz.")
    await ctx.send("Kurulum yapılırken herhangi bir ayarlama yapmayınız!!!!!")

    time.sleep(delay)
    
    """Delete All Role"""
    for role in ctx.guild.roles:  
        try:
            await role.delete()
        except:
            await ctx.send(f"Cannot delete {role.name}")
   
    """Delete All(Channel, Category)"""
    for channel in ctx.guild.channels:
        await channel.delete()
        
    

    overwrites = {
                ctx.message.guild.default_role: discord.PermissionOverwrite(read_messages = False),
                ctx.message.guild.me: discord.PermissionOverwrite(read_messages=True),
                }
    await ctx.message.guild.create_text_channel(name="Setup Satatus Channel", overwrites=overwrites)
    _channel = getChannel("setup-satatus-channel")

   
    """Create New Discord Server"""
    with open('settings/Setup.json', 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
   
  
    for role in data["Role"]:
        per = discord.Permissions(**role["permissions"])
        _role: discord.Role = await ctx.guild.create_role(name=role["name"], permissions=per, mentionable =role["mentionable"],  hoist=role["hoist"])
      
        embed=discord.Embed(title="Oluşturulan Yeni Role", description=_role, color=0xdf1c07, type="rich")
        await _channel.send(embed=embed)

        for ct  in role["Category"]:
            overwrites = {
            _role: discord.PermissionOverwrite(**role["permissions"]),
            ctx.message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.message.guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            _category = await ctx.message.guild.create_category(ct["name"], overwrites=overwrites)
            
            embed=discord.Embed(title="Oluşturulan Yeni Category", description=_category, color=0xb906bc, type="rich")
            await _channel.send(embed=embed)

            for channel in ct["Channels"]:
                # overwrites = {
                # ctx.message.guild.default_role: discord.PermissionOverwrite(read_messages=channel["permissions"]),
                # ctx.message.guild.me: discord.PermissionOverwrite(read_messages=True),
                # }
                # Gerek kalmadı çünkü kanal eklendiği kategorini ile senkronize edildiği zaman kategorinin izinleri kanalda da geçerli oluyor.
                await ctx.message.guild.create_text_channel(name=channel["name"],
                category=_category, topic=channel["topic"], slowmode_delay=channel["slowmode_delay"])
               
                embed=discord.Embed(title="Oluşturulan Yeni Channel", description=channel["name"], color=0x1caf08, type="rich")
                await _channel.send(embed=embed)

  

    """Default User Setup"""
    for cate in data["DefaultUser"]:
        overwrites = {
            ctx.message.guild.default_role: discord.PermissionOverwrite(**cate["permissions"]),
            ctx.message.guild.me: discord.PermissionOverwrite(read_messages=True)
            }

        _category = await ctx.message.guild.create_category(cate["CategoryName"], overwrites=overwrites)

        for channel in cate["Channels"]:
            await ctx.message.guild.create_text_channel(name=channel["name"], overwrites=overwrites,
                category=_category, topic=channel["topic"], slowmode_delay=channel["slowmode_delay"])

    embed=discord.Embed(title="Default User Setup", description="Yeni gelen kullanıcı modülü oluşturuldu", color=0xb906bc, type="rich")
    await _channel.send(embed=embed)


    embed=discord.Embed(title="Server kurulum Bitti", description="Statndart kurulum bitti", color=0x0d13ba, type="rich")
    embed.set_footer(text="Bu kanal 1 dakika içinde kendini sunucudan silecektir!")
    await _channel.send(embed=embed)
    
    time.sleep(60)
    await _channel.delete()

def getChannel(_name):
    for c in Bot.get_all_channels():
        if c.name == _name:
            return c


async def main():
    async with Bot:
        await Bot.start(TOKEN)

asyncio.run(main())
