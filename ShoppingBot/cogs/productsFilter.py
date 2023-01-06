import discord
from discord.ext import commands

from Design.views import *
from Models.products import UserActions


class productsFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def clear(self, ctx: commands.context.Context, amount: int):
        await ctx.channel.purge(limit=amount)

    
    @commands.command()
    async def thisChannel(self, ctx: commands.context.Context):
        """
        Alışverişi başlatacak button u başlatan komut.
        """ 

        async for message in ctx.channel.history(limit=None):
            await message.delete()

        weiv = View()
        weiv.add_item(StartButton(style=discord.ButtonStyle.primary))
        _e = discord.Embed(title="Start Menu Info", color=0x3498db, description=f"Alışveriş ve diğer işlemler için tıklayın.")
        await ctx.send(view=weiv, embed=_e)
        



    @commands.command()
    async def start(self, ctx: commands.context.Context):
        """
        Alışverişi başlatan Select Menu yü başlatır.
        """ 

        user = UserActions(DiscordID=ctx.author.id)
        if user.UserAccData():
            if user.AccessTokenStatus:
                view = FilterView(UserAccessToken=user.AccessToken)
                e = self.infoEmbed(title="Menü info", description="Yapmak istediğiniz işlemi seçiniz", color=0x3498db)
                await ctx.send(view=view, embed=e)

            else:
                await ctx.send("Ilgili firmaya olan erişim pasif halde‼, aktifleştirip tekrar deneyiniz.🙃")
        else:
            await ctx.send("Ilgili firmada herhangi bir hesap erişimi girilmemiş.🥲")



    def infoEmbed(self, title:str, description:str, color: int):
        """
        FilterView's embed
        """
        e = discord.Embed(title=title, color=int(color), description=description, type="rich")
        return e



async def setup(bot):
    await bot.add_cog(productsFilter(bot))