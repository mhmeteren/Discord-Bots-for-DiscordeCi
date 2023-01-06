import discord
from discord.ui import Button, View, Select

from Models.products import  UserProductList
from Models.functions import settings_api
from .ProductModal import *


import locale
import asyncio
from decimal import Decimal


"""Kullanıcının Kaydetiği Urun Listelerinin Discord Tarafında Listelendiği Class(lar) [Begin]"""

class ProductListView(View):
    def __init__(self, UserAccessToken:str):
        super().__init__()
        self.UserAccessToken = UserAccessToken
        self.add_item(ListSelect(UserAccessToken=UserAccessToken))

    async def on_error(self, interaction: discord.Integration, error, item):
        await interaction.response.edit_message(content = str(error))


class ListSelect(Select):
    """
    Kullanıcıya ait ürün listelerinin çekilip Select menü içinde sıralandığı Select class ı
    """
    def __init__(self, UserAccessToken:str):
        super().__init__()
        self.UserAccessToken = UserAccessToken
        self.getProductLists()
        self.options=[
            discord.SelectOption(label=r["UyeListADI"], emoji="📜", value=r["UyeListADI"])
            for r in self.result
        ]

    def getProductLists(self):
        prl = UserProductList(UserAccessToken=self.UserAccessToken)
        result = prl.get_All_ProductList()
        self.result = result


    async def callback(self, interaction:discord.Integration):
        usr_vwr = UserListViewer()
        await usr_vwr.getProduct(interaction=interaction, UserAccessToken=self.UserAccessToken, listname=self.values[0])



class UserListViewer:
    """
    İlgili user listesindeki ürünleri API ile çekip uygun bir arayüzle kullanıcıya sunma class ı
    """

    def createFilterEmbed(self, title:str, description:str, color: int):
        """
        Liste sıralama sonunda çıkan embed
        """
        e = discord.Embed(title=title, color=int(color), description=description, type="rich")
        return e


    def ConvertFiyat(self, fiyat):
        """
        Urun fiyat dönüştürme: 13999.00 => 13.999,00
        """
        locale.setlocale(locale.LC_ALL, 'de_DE')
        return locale.format_string('%.2f', Decimal(fiyat), True)



    async def getProduct(self, interaction: discord.Interaction, UserAccessToken: str, listname: str):
        """
        Girilen değerlere göre Ürünlerin API ile çekilip ilgili arayüzlerle discord tarafında listelendiği fonksiyon.
        """
        await interaction.response.defer(ephemeral=True, thinking=False)
        product = UserProductList(listname=listname, UserAccessToken=UserAccessToken)
        status = product.ProductList()
        if status:
            results = status["UrunList"]
            if results == []:
                notFoundEmbed = self.createFilterEmbed(title=f"**{listname}** Listesi!", description="İstenen listede ürün bulunmamaktadır.", color=0x992d22)
                await interaction.guild.get_channel(interaction.channel_id).send(embed=notFoundEmbed)
            
            else:
                for _product in results:
                    pr = _product["Urun"]
                    ID = pr["UrunID"]
                    UrunADI = pr["UrunADI"]
                    UrunKODU = pr["UrunKODU"]
                    UrunFIYAT = self.ConvertFiyat(pr["UrunFIYAT"])
                    Marka = pr["Marka"]["MarkaADI"]
                    resimList = pr["resimler"]
                    resimler = resimList[0]["UrunImgUrl"]
                    Firma = pr["Firma"]["FirmaADI"]

                    e = discord.Embed(title=Firma)
                    e.add_field(name="Urun Adı", value=UrunADI, inline=False)
                    e.add_field(name="Urun Kodu", value=UrunKODU, inline=False)
                    e.add_field(name="Marka", value=Marka, inline=False)
                    e.add_field(name="Fiyat", value=f"{UrunFIYAT} TL", inline=False)
                    e.set_image(url=f"{resimler}")

                    product_detail_url = settings_api["productDetail"]
                    view = View()
                    view.add_item(ProductButton(label="Ürün", style=discord.ButtonStyle.green, embed=e))
                    view.add_item(PropertiesButton(label="Ürün Ozelikleri", style=discord.ButtonStyle.green, title =UrunADI, OzList=pr["ozellikler"]))
                    view.add_item(DescriptionButton(label="Ürün Acıklaması", style=discord.ButtonStyle.green, title =UrunADI,desc=pr["UrunACIKLAMA"]))
                    view.add_item(ProductImgLeftButton(style=discord.ButtonStyle.primary, imgUrlList=resimList))
                    view.add_item(ProductImgRightButton(style=discord.ButtonStyle.primary, imgUrlList=resimList))
                    view.add_item(DeleteProductToListButton(style=discord.ButtonStyle.gray, embed=e, UrunID=ID, UserAccessToken=UserAccessToken, listname=listname))
                    view.add_item(AddCartButton(style=discord.ButtonStyle.green, label="Sepete Ekle", embed=e, UrunID=ID, UserAccessToken=UserAccessToken))
                    view.add_item(Button(label="Ürün sayfasına git", style=discord.ButtonStyle.link, url=f"{product_detail_url}{ID}/"))

                    await asyncio.sleep(0.5)
                    await interaction.guild.get_channel(interaction.channel_id).send(embed=e, view=view)

                
                await asyncio.sleep(0.3)
                ListStatusEmbed = self.createFilterEmbed(title="Liste Bilgi", description=f"**{listname}** Listeside {len(results)} tane ürün bulundu ve listelendi.", color=0x3498db)
                await interaction.guild.get_channel(interaction.channel_id).send(embed=ListStatusEmbed)
 



class DeleteProductToListButton(Button):
    """
    İlgili Ürünü ilgili listeden silme Buttonu 
    """
    def __init__(self, style: discord.ButtonStyle, embed: discord.Embed, UrunID: int, UserAccessToken: str, listname: str):
        super().__init__(style=style, emoji="💔")
        self.embed = embed
        self.UrunID = UrunID
        self.UserAccessToken = UserAccessToken
        self.listName = listname

    async def callback(self, interaction: discord.Interaction):
        product = ProductListAction(
        listname=self.listName,
        UrunId=self.UrunID,
        UserAccessToken=self.UserAccessToken
        )

        embeds = [self.embed]
        e = discord.Embed(title=f"**{self.listName}** Listesi Ürün Durum", color=int(0xe43725))
        status = product.DeleteFromList()
        e.description = "Urun Listeden çıkartıldı. 🥲" if status else "Bir hata oluştu, daha sonra tekrar deneyin. 🙃"

        embeds.append(e)
        await interaction.response.edit_message(embeds=embeds)
        self.control = not self.control




"""Kullanıcının Kaydetiği Urun Listelerinin Discord Tarafında Listelendiği Alan [End]"""