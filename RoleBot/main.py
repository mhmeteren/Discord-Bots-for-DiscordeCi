import asyncio
import json
import time
import os 

import discord
from discord.ext import commands, tasks
from discord.utils import get

from Model.model import *
from Model.functions import *

intents = discord.Intents.all()
Bot = commands.Bot(command_prefix='!', intents = intents)
TOKEN = os.environ.get('TOKEN') or settings["TOKEN"]

RolesEmoji = []
RolesEmojiForBrand = []
delay = 5


@Bot.event
async def on_ready():
    UyeAccisDead.start()
    await Bot.change_presence(activity=discord.Game(name="Counter Strike 1.6"))
    print("i'm ready")


@Bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return

    if payload.channel_id == CchannelID:
        for role, em in RolesEmoji:
            if em == str(payload.emoji):
                await payload.member.add_roles(role)
                return

    if payload.channel_id == BchannelID:
        for role, em in RolesEmojiForBrand:
            if em == str(payload.emoji):
                await payload.member.add_roles(role)
                return

@Bot.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id == CchannelID:
        guild = Bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        for role, em in RolesEmoji:
            if em == str(payload.emoji):
                await member.remove_roles(role)
                return

    if payload.channel_id == BchannelID:
        guild = Bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        for role, em in RolesEmojiForBrand:
            if em == str(payload.emoji):
                await member.remove_roles(role)
                return


@Bot.event
async def on_command_error(ctx, error):
    print(error)
    print(type(error))

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Böyle bir komut yok!")

    if isinstance(error, commands.MissingRole) or isinstance(error, commands.MissingPermissions):
        await ctx.send("Bu komutu kulanmak icin gerekli yetkiye sahip değilsiniz!!!!")


"""
İlgili firmada hesabı olup da sunucuya yeni katılan kullanıcıların
yetkilendirilmesi
"""
@Bot.event
async def on_member_join(member):
    dc_list = UyeAccPerm()
    if dc_list.getDiscordList():
        if str(member.id) in dc_list.DiscordList:
            for _role in settings["UserRole"]:
                _r = getRoleForMember(member.guild, _role)
                await member.add_roles(_r)


@Bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Böyle bir komut yok!")
          

def getRoleForMember(guild, _name):
    for role in guild.roles:  
        if role.name == _name:
            return role
    return None



def getChannel(_name):
    for c in Bot.get_all_channels():
        if c.name == _name:
            return c
    return None


@Bot.command()
@commands.has_permissions(manage_roles=True) 
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)


@Bot.command()
@commands.has_permissions(manage_roles=True) 
async def setupRoles(ctx):
    await deleteRole(ctx)

    with open('BotSettings/OtherRoles.json', 'r', encoding='utf-8') as f:
        OtherRoles = json.loads(f.read())

    
    overwrites = {
                ctx.message.guild.default_role: discord.PermissionOverwrite(read_messages = False),
                ctx.message.guild.me: discord.PermissionOverwrite(read_messages=True),
                }
    await ctx.message.guild.create_text_channel(name="Setup Satatus Channel", overwrites=overwrites)
    _channel = getChannel("setup-satatus-channel")
    CatogoryChannel = getChannel(settings["CategoryChannel"])
    async for message in CatogoryChannel.history(limit=None):
        await message.delete()

    global CchannelID 
    CchannelID = CatogoryChannel.id

    for role in OtherRoles["Categories"]:
        embed=getEmbed(role["subCategories"], role["name"])
        mesaage = await CatogoryChannel.send(embed=embed)
        for r, _reactions in role["subCategories"]:
            _role: discord.Role = await ctx.guild.create_role(name=r, mentionable =True,  hoist=False)
            await mesaage.add_reaction(_reactions)

            Embed=discord.Embed(title="Oluşturulan Yeni Role", description=r, color=0xdf1c07, type="rich")
            await _channel.send(embed=Embed)
            RolesEmoji.append([_role, _reactions])



    BrandChannel = getChannel(settings["BrandsChannel"])
    async for message in BrandChannel.history(limit=None):
        await message.delete()

    global BchannelID 
    BchannelID = BrandChannel.id

    for role in OtherRoles["Brands"]:
        embed=getEmbed(role["brandlist"], role["name"])
        mesaage = await BrandChannel.send(embed=embed)
        for r, _reactions in role["brandlist"]:
            _role: discord.Role = await ctx.guild.create_role(name=r, mentionable =True,  hoist=False)
            await mesaage.add_reaction(_reactions)

            Embed=discord.Embed(title="Oluşturulan Yeni Role", description=r, color=0xff7b00, type="rich")
            await _channel.send(embed=Embed)
            RolesEmojiForBrand.append([_role, _reactions])


    embed=discord.Embed(title="Server kurulum Bitti", description="Role kurulumu bitti", color=0x0d13ba, type="rich")
    embed.set_footer(text="Bu kanal 10 saniye içinde kendini sunucudan silecektir!")
    await _channel.send(embed=embed)
    time.sleep(10)
    await _channel.delete()


def getEmbed(em, _name):
    embed=discord.Embed(title=_name, description="Bildirim Almak istediginiz Role ait tepiye tıklayın", color=0xb906bc, type="rich")
    
    for _e, _reactions in em:
        embed.add_field(name =_e+" "+_reactions, value="⬆", inline=False)
    return embed


@Bot.command()
@commands.has_permissions(manage_roles=True) 
async def deleteRole(ctx):
    for role in ctx.guild.roles:  
        try:
            if role.name.startswith("#"):
                await role.delete()
        except:
            await ctx.send(f"Cannot delete {role.name}")


@Bot.command()
@commands.has_permissions(manage_roles=True) 
async def reloadRole(ctx):
    with open('BotSettings/OtherRoles.json', 'r', encoding='utf-8') as f:
        OtherRoles = json.loads(f.read())

    overwrites = {
                ctx.message.guild.default_role: discord.PermissionOverwrite(read_messages = False),
                ctx.message.guild.me: discord.PermissionOverwrite(read_messages=True),
                }
    await ctx.message.guild.create_text_channel(name="Setup Satatus Channel", overwrites=overwrites)
    _channel = getChannel("setup-satatus-channel")
    CatogoryChannel = getChannel(settings["CategoryChannel"])

    global CchannelID 
    CchannelID = CatogoryChannel.id

    for role in OtherRoles["Categories"]:
        for r, _reactions in role["subCategories"]:
            _role = getRole(ctx, r)
            if not _role:
                embed=discord.Embed(title="Server kurulum Hatası!", description="Ilglı roler eksik, lütfen roleri tekrar kurunuz!", color=0xdf1c07, type="rich")
                embed.set_footer(text="Bu kanal 10 saniye içinde kendini sunucudan silecektir!")
                await _channel.send(embed=embed)
                time.sleep(10)
                await _channel.delete()
                return

            RolesEmoji.append([_role, _reactions])  

    BrandChannel = getChannel(settings["BrandsChannel"])
    global BchannelID 
    BchannelID = BrandChannel.id

    for role in OtherRoles["Brands"]:
        for r, _reactions in role["brandlist"]:
            _role = getRole(ctx, r)
            if not _role:
                embed=discord.Embed(title="Server kurulum Hatası!", description="Ilglı roler eksik, lütfen roleri tekrar kurunuz!", color=0xdf1c07, type="rich")
                embed.set_footer(text="Bu kanal 10 saniye içinde kendini sunucudan silecektir!")
                await _channel.send(embed=embed)
                time.sleep(10)
                await _channel.delete()
                return

            RolesEmojiForBrand.append([_role, _reactions]) 

    embed=discord.Embed(title="Roler Kayıt Durum", description="Role Aktarımı bitti, her ihtimale karsı test edin veya yeniden kurun!", color=0x0d13ba, type="rich")
    embed.set_footer(text="Bu kanal 10 saniye içinde kendini sunucudan silecektir!")
    await _channel.send(embed=embed)
    time.sleep(10)
    await _channel.delete()


def getRole(ctx, _name):
    for role in ctx.guild.roles:  
        if role.name == _name:
            return role
    return None



"""
Kullanılmayan hesapların yetkilerini silme
"""
@tasks.loop(seconds=10)
async def UyeAccisDead():
    users = UyeDeadAcc()
    users.getDeadList()
    if users.DeadList:
        for u in users.DeadList:
            _user = get(Bot.get_all_members(), id=int(u["DiscordID"]))
            print(f'UyeAccisDead=>{_user}')
            if _user:
                for i in _user.roles:
                    try:
                        await _user.remove_roles(i)
                    except:
                        print(f"Can't remove the role {i}")

        users.DeleteDeadList()




async def main():
    async with Bot:
        await Bot.start(TOKEN)

asyncio.run(main())


