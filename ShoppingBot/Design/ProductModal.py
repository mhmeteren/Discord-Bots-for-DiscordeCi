import discord
from discord.ui import Button, View, Modal, TextInput

from Models.products import Product, ProductListAction, UserCart
from Models.functions import settings_api

import locale
import asyncio
from decimal import Decimal


"""Urun Çekme / Listeleme / Sepete Ekleme - Çıkartma / Favorilere Ekleme - Çıkartma / Özelliklerini Inceleme / Ek Açıklamaya Bakma [Begin]"""

class ProductModal(Modal, title="Product Filter"):
    URUN_ADI = TextInput(label="Urünün adını giriniz.", placeholder="laptop...", style=discord.TextStyle.short, required=False, max_length=100)
    URUN_KODU = TextInput(label="Ürün kodu giriniz.", placeholder="abc123...", style=discord.TextStyle.short, required=False, max_length=50)
    URUN_MIN_FIYAT = TextInput(label="Min. fiyat aralığını giriniz.", placeholder="12345.00", style=discord.TextStyle.short, required=False, max_length=18)
    URUN_MAX_FIYAT = TextInput(label="Max. fiyat aralığını giriniz.", placeholder="54321.00", style=discord.TextStyle.short, required=False, max_length=18)
    
    def __init__(self, UserAccessToken):
        super().__init__()
        self.UserAccessToken = UserAccessToken


    async def on_submit(self, interaction: discord.Integration):
        await self.getProduct(interaction=interaction, page=1, page_size=10, UserAccessToken=self.UserAccessToken, UrunADI__icontains=str(self.URUN_ADI), UrunKODU=str(self.URUN_KODU), UrunFIYAT__range=[str(self.URUN_MIN_FIYAT), str(self.URUN_MAX_FIYAT)])


    """
    Burayı değitir. hatayı direkt mesajda yolama !
    """
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.guild.get_channel(interaction.channel_id).send(f'<@{interaction.user.id}>, Error: {str(error)}')


    def ConvertFiyat(self, fiyat):
        """
        Urun fiyat dönüştürme: 13999.00 => 13.999,00
        """
        locale.setlocale(locale.LC_ALL, 'de_DE')
        return locale.format_string('%.2f', Decimal(fiyat), True)


    def createFilterEmbed(self, title:str, description:str, color: int, **filtre):
        """
        Filtre ile sıralanan ürünlerin sonunda veya ürün bulunamadığı zaman çıkan embed
        """
        e = discord.Embed(title=title, color=int(color), description=description, type="rich")
        e.add_field(name="Urun Adı", value=str(filtre["UrunADI__icontains"]) if str(filtre["UrunADI__icontains"]) != '' else "Ürün adı girilmedi", inline=False)
        e.add_field(name="Urun Kodu", value=str(filtre["UrunKODU"]) if str(filtre["UrunKODU"]) != '' else "Ürün kodu girilmedi", inline=False)
        e.add_field(name="Urun min. fiyat", value=str(filtre["UrunFIYAT__range"][0]) if str(filtre["UrunFIYAT__range"][0]) != '' else "Ürün min. fiyat girilmedi", inline=False)
        e.add_field(name="Urun max. fiyat", value=str(filtre["UrunFIYAT__range"][1]) if str(filtre["UrunFIYAT__range"][1]) != '' else "Ürün max. fiyat girilmedi", inline=False)
        return e


    def productsControl(self, product: Product):
        """
            Aranan özelliklerde başka ürün var mı? Onun kontrolü
        """
        product.page = product.page+1
        return product.getProduct()


    async def getProduct(self, interaction: discord.Interaction, page: int, page_size: int, UserAccessToken: str, **kwargs):
        """
        Girilen değerlere göre Ürünlerin API ile çekilip ilgili arayüzlerle discord tarafında listelendiği fonksiyon.
        """
        await interaction.response.defer(ephemeral=True, thinking=False)
        product = Product(page=page, page_size=page_size, UserAccessToken=UserAccessToken)
        product.convertJSON(**kwargs)
        if product.getProduct():
            results = product.productList["results"]
            count = product.productList["count"]
            if count == 0:
                notFoundEmbed = self.createFilterEmbed(title="Ürün Bulunamadı!", description="Girilen özelliklerde ürün bulunamadı.", color=0x992d22, **kwargs)
                await interaction.guild.get_channel(interaction.channel_id).send(embed=notFoundEmbed)
            
            else:
                for _product in results:
                    pr = _product
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
                    view.add_item(AddFavoriteButton(style=discord.ButtonStyle.gray, embed=e, UrunID=ID, UserAccessToken=UserAccessToken))
                    view.add_item(AddCartButton(style=discord.ButtonStyle.green, label="Sepete Ekle", embed=e, UrunID=ID, UserAccessToken=UserAccessToken))
                    view.add_item(Button(label="Ürün sayfasına git", style=discord.ButtonStyle.link, url=f"{product_detail_url}{ID}/"))

                    await asyncio.sleep(0.5)
                    await interaction.guild.get_channel(interaction.channel_id).send(embed=e, view=view)

                await asyncio.sleep(0.3)
                FilterStatusEmbed = self.createFilterEmbed(title="Filtre Durum", description=f"Girilen değerlere uyan {len(results)} tane ürün bulundu.\nAradığınız ürünü bulamadıysanız, ardığınız ürünün özeliklerini ayrıntılandırarak aratın", color=0x3498db, **kwargs)
                FilterStatusView = View()
                if self.productsControl(product):
                    FilterStatusEmbed.description = FilterStatusEmbed.description + " veya 'Daha Fazla Ürün' butonu ile diğer seçenekleri görebilirsiniz."
                    FilterStatusView.add_item(MoreProductsButton(style=discord.ButtonStyle.primary, label="Daha Fazla Ürün", page=page+1, page_size=page_size, UserAccessToken=UserAccessToken, **kwargs))
                else:
                    FilterStatusEmbed.description = FilterStatusEmbed.description + ".\n \n Bulabildiğim ürünler bu kadar. 🥲"
                await interaction.guild.get_channel(interaction.channel_id).send(embed=FilterStatusEmbed, view=FilterStatusView)




class MoreProductsButton(Button, ProductModal):
    """
    Daha fazla ürün listelemek için 'Daha Fazla Ürün' buttonu
    """
    def __init__(self, style: discord.ButtonStyle, label: str, page: int, page_size: int, UserAccessToken: str, **kwargs):
        super().__init__(style=style, emoji="🔃", label=label)
        self.page = page
        self.page_size = page_size
        self.UserAccessToken = UserAccessToken
        self.kwargs = kwargs

    
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        await interaction.message.edit(view=self.view)
        await self.getProduct(interaction=interaction, page=self.page, page_size=self.page_size, UserAccessToken=self.UserAccessToken, **self.kwargs)



class AddCartButton(Button):
    """
    İlgili Ürünü ilgili kullanıcının sepetine kaydetmek için 'Sepete Ekle' Buttonu
    """
    def __init__(self, style: discord.ButtonStyle, label: str, embed: discord.Embed, UrunID: int, UserAccessToken: str):
        super().__init__(style=style, emoji="🛒", label=label)
        self.embed = embed
        self.UrunID = UrunID
        self.UserAccessToken = UserAccessToken

    async def callback(self, interaction: discord.Interaction):
        # await interaction.response.edit_message(embed=self.embed)
        await interaction.response.send_modal(AddCartModal(UserAccessToken=self.UserAccessToken, UrunID=self.UrunID, embed=self.embed))



class AddCartModal(Modal, title="Sepete Ekle"):
    URUN_ADET = TextInput(label="Almak istediğiniz ürünün adedini girin", placeholder="kaç adet istersiniz", style=discord.TextStyle.short, required=True, max_length=3, default='1')

    def __init__(self, UserAccessToken, UrunID: int, embed: discord.Embed):
        super().__init__()
        self.UserAccessToken = UserAccessToken
        self.UrunID = UrunID
        self.embed = embed

    async def on_submit(self, interaction: discord.Integration):
        embeds = [self.embed]
        try:
            adet = int(str(self.URUN_ADET))
            e = discord.Embed(title="Sepet info", color=0x3498db, description=f"Üründen {adet} adet sepete eklendi", type="rich")
            
            userCart = UserCart(UserAccessToken=self.UserAccessToken)
            AddCartStatus = userCart.addCart(UrunId=self.UrunID, UrunADET=adet)
            if not AddCartStatus:
                e.description = "Bir hata oluştu daha sonra tekrar deneyin. 🙃"
                e.color = 0x992d22
            embeds.append(e)
        except ValueError:
            e = discord.Embed(title="Sepet info", color=0x992d22, description=f"<@{interaction.user.id}>, Urun adedi olarak **{self.URUN_ADET}** girdiniz, lütfen sadece numerik değer giriniz‼️", type="rich")
            embeds.append(e)

        await interaction.response.edit_message(embeds = embeds)


    """
    Burayı değitir. hatayi direkt mesajda yolama !
    """
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.guild.get_channel(interaction.channel_id).send(f'<@{interaction.user.id}>, Error: {str(error)}')



class AddFavoriteButton(Button):
    """
    İlgili Ürünü ilgili kullanıcının favorilerine eklemek için '❤️' buttonu
    """
    def __init__(self, style: discord.ButtonStyle, embed: discord.Embed, UrunID: int, UserAccessToken: str):
        super().__init__(style=style, emoji="❤️")
        self.embed = embed
        self.UrunID = UrunID
        self.UserAccessToken = UserAccessToken
        self.listName = "Favoriler"
        self.control = False

    async def callback(self, interaction: discord.Interaction):
        product = ProductListAction(
        listname=self.listName,
        UrunId=self.UrunID,
        UserAccessToken=self.UserAccessToken
        )
        embeds = [self.embed]
        e = discord.Embed(title="Favoriler", color=int(0xe43725))

        if self.control:
            status = product.DeleteFromList()
            e.description = "Urun Favorilerinden çıkartıldı. 🥲" if status else "Bir hata oluştu, daha sonra tekrar deneyin. 🙃"
        else:
            status = product.AddFromList()
            e.description = "Urun Favorilerine eklendi 💖" if status else "Urun Favorilerine eklenemedi. Daha önce eklenmiş olabilir. 🙃"

        embeds.append(e)
        await interaction.response.edit_message(embeds=embeds)
        self.control = not self.control



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


"""Urun Çekme / Listeleme / Sepete Ekleme - Çıkartma / Favorilere Ekleme - Çıkartma / Özelliklerini Inceleme / Ek Açıklamaya Bakma [End]"""
