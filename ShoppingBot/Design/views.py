import discord
from discord.ui import Button, View, Select

from Models.products import UserActions
from Models.functions import settings_api


from .ProductModal import ProductModal
from .ProductListView import ProductListView
from .ProductUserCart import UserCartViewer


class FilterView(View):
    """
    Ilk başta kullanıcının yapmak istediği işlemi seçtiği ve içinde Select menü nün bulunduğu class
    """
    def __init__(self, UserAccessToken):
        super().__init__()
        self.UserAccessToken = UserAccessToken

    @discord.ui.select(placeholder="Choose a item",
            options=[
            discord.SelectOption(label="Urun ara", emoji="🤩", description="Urün arama menüsü.", value="0x01"),
            # discord.SelectOption(label="Filtre ile urun ara", emoji="🤨", description="Urunleri filtreleme menüsü.", value="0x02"),
            discord.SelectOption(label="Sepetim", emoji="🛒", description="Urun sepetini listeler.", value="0x03"),
            discord.SelectOption(label="Listelerim", emoji="📜", description="Urun Listelerini gösterir.", value="0x04")
        ])
    async def callback(self, interaction: discord.Integration, select: Select):
        match select.values[0]:
            case "0x01":
                await interaction.response.send_modal(ProductModal(UserAccessToken=self.UserAccessToken))
            # case "0x02":
            #     await interaction.response.send_message(f"You choose : {select.values}")
            case "0x03":
                sp = UserCartViewer()
                await sp.getProduct(interaction=interaction, UserAccessToken=self.UserAccessToken)  
            case "0x04":
                await interaction.response.send_message(content="Listelemek Istediğiniz Listeyi Secin", view = ProductListView(UserAccessToken=self.UserAccessToken))


        weiv = View()
        weiv.add_item(MainManuButton(style=discord.ButtonStyle.primary, DiscordID=interaction.user.id))
        _e = discord.Embed(title="Menu Info", color=0x3498db, description=f"Kanalı sıfırlamak ve ana menüye dönemk için tıklayın.")
        await interaction.guild.get_channel(interaction.channel_id).send(view=weiv, embed=_e)


    async def on_error(self, interaction: discord.Integration, error, item):
        await interaction.response.edit_message(content = str(error))




class MainManuButton(Button):
    """
    En başta çıkan ana menüyü tekrar gösterir
    """
    def __init__(self, style: discord.ButtonStyle, DiscordID: int):
        super().__init__(style=style, emoji="🔃", label="Ana Menu")
        self.DiscordID = DiscordID


    async def callback(self, interaction: discord.Interaction):
        """
        Kanalı mesajlardan temizle ve ana menüyü tekrar göster/gönder.
        """

        async for message in interaction.channel.history(limit=None):
            await message.delete()

        user = UserActions(DiscordID=self.DiscordID)
        if user.UserAccData():
            if user.AccessTokenStatus:
                view = FilterView(UserAccessToken=user.AccessToken)
                view.add_item(EndButton())
                e = discord.Embed(title="Menü info", description="Yapmak istediğiniz işlemi seçiniz", color=0x3498db)
                await interaction.response.send_message(embed=e, view=view)
            else:
                await interaction.response.send_message("Ilgili firmaya olan erişim pasif halde‼, aktifleştirip tekrar deneyiniz.🙃")
        else:
            await interaction.response.send_message("Ilgili firmada herhangi bir hesap erişimi girilmemiş.🥲")




class StartButton(Button):
    """
    alışveriş veya bir işlem(sepet listelme vb.) başlatma button u
    """
    def __init__(self, style: discord.ButtonStyle):
        super().__init__(style=style, emoji="⭐", label="Başla")


    async def callback(self, interaction: discord.Interaction):
        """
        Islemi baslat ve ilgili kanalları sunucuya ekle.
        """
        Channel = discord.utils.get(interaction.guild.text_channels, name=f"{interaction.user.name} Shopping Channel".replace(" ", "-").lower())
        if Channel:
            await interaction.response.send_message(f"<#{Channel.id}>, Zaten bir alışveriş kanalına sahipsiniz.", ephemeral=True, delete_after=10.0)
            await Channel.send(f'<@{interaction.user.id}> Bu kanal daha önce size ayrılmış')
        else:
            UserPermissions = {
                "administrator": False,
                "add_reactions": False,
                "read_messages": False,
                "send_messages": False,
                "manage_messages": False,   
                "use_application_commands": False,
                "manage_webhooks":False,
                "manage_events":False,
                "manage_threads": False,
                "create_private_threads": False,
                "create_public_threads": False,
                "send_messages_in_threads": False,  
                "view_channel": True,
                "read_message_history": True
            }

            overwrites = {
                interaction.user: discord.PermissionOverwrite(**UserPermissions),
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            _category = await interaction.guild.create_category(name=f"{interaction.user.name} | Shopping Category", overwrites=overwrites)
            _channel = await interaction.guild.create_text_channel(name=f"{interaction.user.name} Shopping Channel", category=_category, topic="Kullanıcı alisveris kanali")
            await _channel.send(f'<@{interaction.user.id}> Size özel ve güvenli kanalda alışverişin tadını çıkartın ❤️.')
            weiv = View()
            weiv.add_item(MainManuButton(style=discord.ButtonStyle.primary, DiscordID=interaction.user.id))
            _e = discord.Embed(title="Menu Info", color=0x3498db, description=f"Alışveriş ve diğer işlemler için tıklayın.")
            await _channel.send(embed=_e, view=weiv)
            await interaction.response.send_message(f"<#{_channel.id}>, Hadi başlıyalım 😎", ephemeral=True, delete_after=10.0)




class EndButton(Button):
    """
    Tüm işlemleri sonlandırıp ilgili kanalları da silek için.
    """
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, emoji="🥲", label="Tüm Işlemi Sonlandır")


    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("bye")
        await interaction.channel.delete()
        await interaction.channel.category.delete()



