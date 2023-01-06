import discord
from discord.ui import Button, View, Modal, TextInput, Select

from Models.products import  UserCart, UyeAccControl, UyeSiparis
from Models.functions import settings_api
from .ProductModal import *


import locale
import asyncio
from decimal import Decimal



"""Kullanıcının Sepetindeki Ürünleri Listeleyen/Sepete Ekleyen/Sepeten Silen Class(lar) [Begin]"""




class UserCartViewer:
    """
    İlgili kullanıcının sepetindeki ürünleri API ile çekip Discord a gerekli arayüzle Listeneme Class ı
    """

    def ConvertFiyat(self, fiyat):
        """
        Urun fiyat dönüştürme: 13999.00 => 13.999,00
        """
        locale.setlocale(locale.LC_ALL, 'de_DE')
        return locale.format_string('%.2f', Decimal(fiyat), True)



    async def getProduct(self, interaction: discord.Interaction, UserAccessToken: str):
        """
        Girilen değerlere göre Ürünlerin API ile çekilip ilgili arayüzlerle discord tarafında listelendiği fonksiyon.
        """
        await interaction.response.defer(ephemeral=True, thinking=False)
        userCart = UserCart( UserAccessToken=UserAccessToken)
        results = userCart.UserCartList()
        if results:
            SepetToplamTutar = Decimal()
            SepetToplamUrunAdet = 0
            for _product in results:
                pr = _product["Urun"]
                SepetID = _product["SepetID"]
                ID = pr["UrunID"]
                UrunADI = pr["UrunADI"]
                UrunKODU = pr["UrunKODU"]
                UrunFIYAT = self.ConvertFiyat(pr["UrunFIYAT"])
                Marka = pr["Marka"]["MarkaADI"]
                resimList = pr["resimler"]
                resimler = resimList[0]["UrunImgUrl"]
                Firma = pr["Firma"]["FirmaADI"]
                UrunADET = _product["UrunADET"]
                SepetToplamUrunAdet = SepetToplamUrunAdet + int(UrunADET)
                SepetToplamTutar = SepetToplamTutar +  (Decimal(pr["UrunFIYAT"]) * int(UrunADET))
                e = discord.Embed(title=Firma)
                e.add_field(name="Urun Adı", value=UrunADI, inline=False)
                e.add_field(name="Urun Kodu", value=UrunKODU, inline=False)
                e.add_field(name="Marka", value=Marka, inline=False)
                e.add_field(name="Fiyat", value=f"{UrunFIYAT} TL", inline=False)
                e.add_field(name="Urun Adedi", value=f"{UrunADET} TANE", inline=False)
                e.set_image(url=f"{resimler}")
                product_detail_url = settings_api["productDetail"]
                view = View()
                view.add_item(ProductButton(label="Ürün", style=discord.ButtonStyle.green, embed=e))
                view.add_item(PropertiesButton(label="Ürün Ozelikleri", style=discord.ButtonStyle.green, title =UrunADI, OzList=pr["ozellikler"]))
                view.add_item(DescriptionButton(label="Ürün Acıklaması", style=discord.ButtonStyle.green, title =UrunADI,desc=pr["UrunACIKLAMA"]))
                view.add_item(ProductImgLeftButton(style=discord.ButtonStyle.primary, imgUrlList=resimList))
                view.add_item(ProductImgRightButton(style=discord.ButtonStyle.primary, imgUrlList=resimList))
                view.add_item(DeleteCartButton(style=discord.ButtonStyle.green, label="Sepeten Çıkart", embed=e, SepetID=SepetID, UserAccessToken=UserAccessToken))
                view.add_item(Button(label="Ürün sayfasına git", style=discord.ButtonStyle.link, url=f"{product_detail_url}{ID}/"))
                await asyncio.sleep(0.7)
                await interaction.guild.get_channel(interaction.channel_id).send(embed=e, view=view)


            await asyncio.sleep(0.3)
            sepetStatusEmbed = discord.Embed(title="Sepet Bilgi", description=f"**Sepette** {len(results)} tane farklı ürün bulundu.", color=0x3498db)
            sepetStatusEmbed.add_field(name="Toplam Ürün adedi", value=f'{SepetToplamUrunAdet} TANE', inline=False)
            sepetStatusEmbed.add_field(name="Sepet Toplam Tutar", value=f'{self.ConvertFiyat(SepetToplamTutar)} TL', inline=False)
            sepetView = View()
            sepetView.add_item(ConfirmCartButton(style=discord.ButtonStyle.green, label="Sepeti Onayla", embed=sepetStatusEmbed, SepetToplamTutar=SepetToplamTutar, UserAccessToken=UserAccessToken))
            await interaction.guild.get_channel(interaction.channel_id).send(embed=sepetStatusEmbed, view=sepetView)

        else:
            await asyncio.sleep(0.3)
            sepetInfo = discord.Embed(title="Sepet Bilgi", description=f"**Sepette** ürün bulunamadı!", color=0x992d22)
            await interaction.guild.get_channel(interaction.channel_id).send(embed=sepetInfo)



class DeleteCartButton(Button):
    """
    İlgili Ürünü ilgili kullanıcının sepetinden silmek için 'Sepeten Çıkart' Buttonu
    """
    def __init__(self, style: discord.ButtonStyle, label: str, embed: discord.Embed, SepetID: int, UserAccessToken: str):
        super().__init__(style=style, emoji="🥲", label=label)
        self.embed = embed
        self.SepetID = SepetID
        self.UserAccessToken = UserAccessToken
        self.control = False

    async def callback(self, interaction: discord.Interaction):
        embeds = [self.embed]
        if not self.control:
            userCart = UserCart( UserAccessToken= self.UserAccessToken)
            e = discord.Embed(title=f"**Sepette** Ürün Durum", color=int(0xe43725))
            status = userCart.UserCartDeleteProduct(pid=self.SepetID)
            e.description = "Urun sepeten çıkartıldı. 🥲" if status else "Bir hata oluştu, daha sonra tekrar deneyin. 🙃"
            self.control = status #*
            embeds.append(e)

            if self.control: #*
                self.view.add_item(CartReload(style=discord.ButtonStyle.primary, label="Sepeti Yenile", UserAccessToken=self.UserAccessToken))
            
        else:
            e = discord.Embed(title=f"**Sepette** Ürün Durum", color=int(0xe43725))
            e.description = "Urun daha önce sepeten çıkartıldı. 🥲" 
            embeds.append(e)


        await interaction.response.edit_message(embeds=embeds, view=self.view)
        



class ConfirmCartButton(Button):
    """
    Sepetten ödeme menüsüne geçiş için 'Sepeti Onayla' Buttonu
    """
    def __init__(self, style: discord.ButtonStyle, label: str, embed: discord.Embed, SepetToplamTutar: Decimal, UserAccessToken: str):
        super().__init__(style=style, emoji="🙃", label=label)
        self.embed = embed
        self.SepetToplamTutar = SepetToplamTutar
        self.UserAccessToken = UserAccessToken

    async def callback(self, interaction: discord.Interaction):
        self.disabled = True

        embeds = [self.embed]
        uyeAccControl = UyeAccControl(DiscordID=interaction.user.id, totalfee=self.SepetToplamTutar)
        data = uyeAccControl.WalletControlAndAddresses()
        if data:
            if "islem" in data:
                msg = data["islem"]["message"]
                embeds.append(discord.Embed(title="Wallet Control Info", description=f"{msg} 🥲", color=0x992d22))
            else:
                if data["UyeAdres"]:
                    e = discord.Embed(title="Adresler", description="Ürünlerin gönderileceği adresi seçiniz", color=0x3498db)
                    view = View()
                    view.add_item(UserAddressListSelect(UserAccessToken=self.UserAccessToken, result=data["UyeAdres"], SepetToplamTutar=self.SepetToplamTutar, UyeWALLET=data["UyeWALLET"]))
                    await interaction.guild.get_channel(interaction.channel_id).send(embed=e, view=view)
                else:
                     embeds.append(discord.Embed(title="Wallet Control Info", description="Cüzdan bakiyeniz yeterli fakat herhangi bir adres bilginiz sistemde mevcut değil.", color=0x992d22))
        else:
            embeds.append(discord.Embed(title="Wallet Control Info", description="Bir hata oluştu lütfen daha sonra tekrar deneyiniz. 🙃", color=0x992d22))
        await interaction.response.edit_message(embeds=embeds, view=self.view)




class UserAddressListSelect(Select):
    """
    Kullanıcıya ait adreslerin listelendiği Select class ı
    """
    def __init__(self, UserAccessToken:str, result: list, SepetToplamTutar: Decimal, UyeWALLET: str):
        super().__init__()
        self.UserAccessToken = UserAccessToken
        self.result = result
        self.SepetToplamTutar = SepetToplamTutar
        self.UyeWALLET = UyeWALLET
        self.options=[
            discord.SelectOption(label=r["UyeAdresBASLIK"], emoji="🏡", value=r["UyeAdresID"], description=r["UyeAdresALICI"])
            for r in self.result
        ]
        self.placeholder = "Bir adres seçin"
        self.control = False


    async def callback(self, interaction:discord.Integration):
        embeds = []
        address = self.getDataINresult(int(self.values[0]))
        if address:
            e = discord.Embed(title=address["UyeAdresBASLIK"], color=0x3498db)
            e.add_field(name="Alıcı Bilgisi", value=address["UyeAdresALICI"], inline=False)
            e.add_field(name="Adres Bilgisi", value=address["UyeAdres"], inline=False)
            e.add_field(name="Alıcı GSM Bilgisi", value=address["UyeAdresALICIGSM"], inline=False)
            e.add_field(name="Alıcı TC Bilgisi", value=f'********{address["UyeAdresALICITC"][-3:]}', inline=False)
            embeds.append(e)
            if not self.control:
                self.control = True
                address = dict(
                ADRES = address["UyeAdres"][:300],
                ADRESBASLIK = address["UyeAdresBASLIK"][:50],
                ADRESALICI = address["UyeAdresALICI"][:50],
                ADRESALICIGSM = address["UyeAdresALICIGSM"][:11],
                ADRESALICITC = address["UyeAdresALICITC"][:11]
                )
                self.view.add_item(
                    CheckoutButton(
                        label="Ödemeyi bittir",
                        style=discord.ButtonStyle.primary,
                        UserAccessToken=self.UserAccessToken,
                        SepetToplam=self.SepetToplamTutar,
                        userWALLET = self.UyeWALLET,
                        **address
                           )
                    )
        else:
            e = discord.Embed(title="Adress Info", color=0x992d22, description="Adresler sıralanırken bir hata oluştu lütfen daha sonra tekrar deneyiniz. 🙃")
            embeds.append(e)
        await interaction.response.edit_message(embeds=embeds, view=self.view)



    def getDataINresult(self, id: int):
        for address in self.result:
            if address["UyeAdresID"] == id:
                return address
        return None 


class CheckoutButton(Button):
    """
    Ödemeyi bittir
    """
    def __init__(self, style: discord.ButtonStyle, label: str,  UserAccessToken: str, SepetToplam: Decimal, userWALLET: Decimal, **address):
        super().__init__(style=style, emoji="✔️", label=label)
        self.UserAccessToken = UserAccessToken
        self.address = address
        self.SepetToplam = SepetToplam
        self.userWALLET = userWALLET




    async def callback(self, interaction: discord.Interaction):
        """
        Seçilen adress bilgileri ile ilgili kullanıcının sanal cüzdanında yeterli bakiye de varsa satın alma işlemini tamamla.
        """
        self.disabled= True
        uyeSiparis = UyeSiparis(UserAccessToken=self.UserAccessToken, DiscordId=interaction.user.id)
        status = uyeSiparis.Checkout(SepetToplam=self.SepetToplam, userWALLET=self.userWALLET, **self.address)

        if status:
            e = discord.Embed(title="Siparis Info", color=0x3498db, description=f"Satın alma işlemi başarılı. 😎")
            await interaction.guild.get_channel(interaction.channel_id).send(embed=e)
        else:
            e = discord.Embed(title="Siparis Info", color=0x992d22, description="Bilgiler aktarılırken bir hata oluştu lütfen daha sonra tekrar deneyiniz. 🙃")
            await interaction.guild.get_channel(interaction.channel_id).send(embed=e)

        await interaction.response.edit_message(view=self.view)



class CartReload(Button):
    """
    Sepetten ürün silime işleminden sonra kullanıcı isterse sepetti tekrar listelemek için.
    """
    def __init__(self, style: discord.ButtonStyle, label: str,  UserAccessToken: str):
        super().__init__(style=style, emoji="🔃", label=label)
        self.UserAccessToken = UserAccessToken

    async def callback(self, interaction: discord.Interaction):
        """
        İlgili kanaldaki tüm mesajları sil ve sepeti tekrar listele
        """
        _channel = interaction.guild.get_channel(interaction.channel_id)
        async for message in _channel.history(limit=None):
            await message.delete()

        sp = UserCartViewer()
        await sp.getProduct(interaction=interaction, UserAccessToken=self.UserAccessToken)


"""Kullanıcının Sepetindeki Ürünleri Listeleyen/Sepete Ekleyen/Sepeten Silen Class(lar) [End]"""