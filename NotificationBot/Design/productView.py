import discord
from discord.ext import commands
from discord.ui import Button, View

from Models.functions import settings_api
from Models.productModel import Product

import locale
import asyncio
from decimal import Decimal




class ProductViewer:
    """
    Kullanıcılara takip etkleri kategorilerin veya markaların ürünlerini API ile çekip Discord a gerekli arayüzle Listeneme Class ı
    """

    def ConvertFiyat(self, fiyat):
        """
        Urun fiyat dönüştürme: 13999.00 => 13.999,00
        """
        locale.setlocale(locale.LC_ALL, 'de_DE')
        return locale.format_string('%.2f', Decimal(fiyat), True)


    
    async def getProduct(self, Txtchannel: discord.TextChannel, page: int, page_size: int, Bot: commands.Bot):
            """
            Onerilecek Urunlerin API ile çekilip, arayüze eklenmesi ve discord a ilgili kanala gösderilemesi
            """
            product = Product(page=page, page_size=page_size)
            if product.getProducts():
                results = product.productList["results"]
                count = product.productList["count"]
                if count == 0:
                    return

                else:
                    for _product in results:
                        pr = _product["OnerilenUrun"]
                        ID = pr["UrunID"]
                        UrunADI = pr["UrunADI"]
                        UrunKODU = pr["UrunKODU"]
                        UrunFIYAT = self.ConvertFiyat(pr["UrunFIYAT"])
                        Marka = pr["Marka"]["MarkaADI"]
                        resimList = pr["resimler"]
                        resimler = resimList[0]["UrunImgUrl"]
                        Firma = pr["Firma"]["FirmaADI"]
                        AltKategoriADI = pr["AltKategori"]["AltKategoriADI"]
                        MarkaADI = pr["Marka"]["MarkaADI"]

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
                        view.add_item(Button(label="Satın Al", style=discord.ButtonStyle.green, emoji="🤑"))
                        view.add_item(Button(label="Ürün sayfasına git", style=discord.ButtonStyle.link, url=f"{product_detail_url}{ID}/"))

                        await asyncio.sleep(0.5)
                        category_role = discord.utils.get(Bot.guilds[0].roles, name=f"#{AltKategoriADI}")
                        brand_role = discord.utils.get(Bot.guilds[0].roles, name=f"#{MarkaADI}")
                        if not brand_role:
                            brand_role = discord.utils.get(Bot.guilds[0].roles, name=f"#{MarkaADI.lower().title()}")
                        await Txtchannel.send(content=f"Kategori: <@&{category_role.id if category_role else ''}>, Marka: <@&{brand_role.id if brand_role else ''}>", embed=e, view=view)
                    product.setProducs()





class ImgEmbed(discord.Embed):
    def __init__(self, title: str, Imgurl):
        super().__init__(title=title)
        self.set_image(url=Imgurl)


imgIndex = 0
class ProductImgRightButton(Button):
    """
    İlgili ürünün görselerine bakmak için '▶️' buttonu
    """
    def __init__(self, style: discord.ButtonStyle, imgUrlList: list):
        super().__init__(style=style, emoji="▶️")
        self.embeds = [ImgEmbed(title="Ürün n. görsel", Imgurl=Imgurl["UrunImgUrl"]) for Imgurl in imgUrlList]


    async def callback(self, interaction: discord.Interaction):
        global imgIndex
        if imgIndex == len(self.embeds)-1:
            imgIndex = 0
        else:
            imgIndex += 1
        self.embeds[imgIndex].title=f"Ürün {imgIndex+1}. görsel"
        await interaction.response.edit_message(embed=self.embeds[imgIndex])



class ProductImgLeftButton(Button):
    """
    İlgili ürünün görselerine bakmak için '◀️' buttonu
    """
    def __init__(self, style: discord.ButtonStyle, imgUrlList: list):
        super().__init__(style=style, emoji="◀️")
        self.embeds = [ImgEmbed(title="Ürün n. görsel", Imgurl=Imgurl["UrunImgUrl"]) for Imgurl in imgUrlList]


    async def callback(self, interaction: discord.Interaction):
        global imgIndex
        if imgIndex == 0:
            imgIndex = len(self.embeds)-1
        else:
            imgIndex -= 1
        self.embeds[imgIndex].title=f"Ürün {imgIndex+1}. görsel"
        await interaction.response.edit_message(embed=self.embeds[imgIndex])



class ProductButton(Button):
    """
    İlk gösterilen ürün bilgilerinin olduğu embed i tekrar görmek için 'Ürün' Buttonu
    """
    def __init__(self, style: discord.ButtonStyle, label, embed: discord.Embed):
        super().__init__(style=style, label=label)
        self.embed = embed
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.embed)



class PropertiesButton(Button):
    """
    İlgili ürünün özelliklerine bakmak için 'Ürün özeelikleri' buttonu
    """
    def __init__(self, style: discord.ButtonStyle, label, title, OzList: list):
        super().__init__(style=style, label=label)
        self.OzList = OzList
        self.title = title
    
    async def callback(self, interaction: discord.Interaction):
        self.control = False
        e = discord.Embed(title=self.title)
        for ozDict in self.OzList:
            e.add_field(name=ozDict["UrunOzType"], value=ozDict["UrunOzValue"], inline=True)
        await interaction.response.edit_message(embed=e)



class DescriptionButton(Button):
    """
    İlgili ürününü açıklamasına bakmak için 'Ürün açıklama' buttonu
    """
    def __init__(self, style: discord.ButtonStyle, label, title, desc: str):
        super().__init__(style=style, label=label)
        self.desc = desc
        self.title = title

    async def callback(self, interaction: discord.Interaction):
        self.control = False
        e = discord.Embed(title=self.title)
        for desc in self.desc.split("|"):
            e.add_field(name=">_", value=desc, inline=False)
        await interaction.response.edit_message(embed=e)

