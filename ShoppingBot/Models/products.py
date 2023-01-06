import requests
import json
from decimal import Decimal
from Models.functions import settings_api, settings_api_deci



class Product:
    """
    UserAccessToken ve filtre ksımında girilen değerlere göre API dan ürün çekme
    """
    def __init__(self, page: int, page_size: int, UserAccessToken: str):
        self.page = page
        self.page_size = page_size
        self.UserAccessToken = UserAccessToken


    def getProduct(self):
        params = {'page': self.page, 'page_size': self.page_size, 'UserAccessToken': self.UserAccessToken}
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        r = requests.get(f'{settings_api["getProduct"]}', params=params, data=self.data, headers=headers)
        if r.status_code == 200:
            self.productList = r.json()
            return True
        return False


    def convertJSON(self, **kwargs):
        Filter = dict()
        for key, value in kwargs.items():
            if value != '':
                Filter[key] = value

        # Fiyat bilgisi girilmemişse
        if Filter["UrunFIYAT__range"][0] == '' and Filter["UrunFIYAT__range"][1] == '':
            del Filter["UrunFIYAT__range"]
            
        # Sadece Max. fiyat girilmişse
        elif Filter["UrunFIYAT__range"][0] == '':
            Filter["UrunFIYAT__lte"] = Filter["UrunFIYAT__range"][1]
            del Filter["UrunFIYAT__range"]
            
        # Sadece Min. fiyat girilmişse
        elif Filter["UrunFIYAT__range"][1] == '':
            Filter["UrunFIYAT__gte"] = Filter["UrunFIYAT__range"][0]
            del Filter["UrunFIYAT__range"]

        # Stokta olan ürünleri ve Durum olarak TRUE olanları getir.    
        Filter["UrunSTOK__gt"] = 0 
        Filter["UrunDURUM"] = True

        self.data = json.dumps(Filter)



class UserActions:
    """
    1 - Kullanıcının DiscordId si ile ilgili firmada erişime açık access token çekme. 
    2 - Ürün favorilere veya diğer kayıt listelerine ekleme/çıkartma/listeleme.
    """
    def __init__(self, DiscordID):
        self.DiscordID = DiscordID
        self.AccessToken = None
        self.AccessTokenStatus = False


    def UserAccData(self):
        params = {'firmaId': settings_api_deci["FirmaID"]}
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        r = requests.get(f'{settings_api_deci["UyeAcc"]}{self.DiscordID}/', params=params, headers=headers)
        if r.status_code == 200:
            data = r.json()
            self.AccessTokenStatus = data["UyeAccDURUM"]
            if data["UyeAccDURUM"]:
                self.AccessToken = data["UyeAccTOKEN"]
            return True
        return False




class ProductListAction:
    def __init__(self, listname: str, UrunId: int, UserAccessToken: str):
        self.listname = listname
        self.UrunId = UrunId
        self.UserAccessToken = UserAccessToken

    def AddFromList(self):
        """
        Ilgili listeye ilgili ürünü ekleme.
        """
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        data = dict(
            Urun=self.UrunId,
            Token=self.UserAccessToken
        )
        url = f'{settings_api["plists"]}{self.listname}/'
        data = json.dumps(data)
        r = requests.post(url=url, data=data, headers=headers)
        if r.status_code == 201:
            return True
        return False


    def DeleteFromList(self):
        """
        Ilgili listeden ilgili ürünü silme.
        """
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        data = dict(
            Token=self.UserAccessToken
        )
        params = {"p": self.UrunId}
        url = f'{settings_api["plists"]}{self.listname}/'
        data = json.dumps(data)
        r = requests.delete(url=url, data=data, headers=headers, params=params)
        if r.status_code == 204:
            return True
        return False
    


class UserProductList:
    """
    Kullanıcıya ait Urun Listelerini Sıralandığı / Listelerin içindeki ürünlerin listelendiği class
    """
    def __init__(self, listname: str=None, UserAccessToken: str=None):
        self.listname = listname
        self.UserAccessToken = UserAccessToken

    def ProductList(self):
        """
        Ilgili listede bulunan tüm ürünleri çekme.
        """
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        data = dict(
            Token=self.UserAccessToken
        )
        url = f'{settings_api["plists"]}{self.listname}/'
        data = json.dumps(data)
        r = requests.get(url=url, data=data, headers=headers)
        if r.status_code == 200:
            return r.json()
        return False
    

    def get_All_ProductList(self):
        """
        Ilgılı kullanıcının sahip olduğu tüm ürün listelerini çekme.
        """
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        data = dict(
            Token=self.UserAccessToken
        )
        url = f'{settings_api["userplists"]}'
        data = json.dumps(data)
        r = requests.get(url=url, data=data, headers=headers)
        if r.status_code == 200:
            return r.json()
        return False


class UserCart:
    """
    Kullanıcının sepetindeki Urunlerin Listelendiği/Eklendiği/Silindiği Class
    """
    def __init__(self, UserAccessToken: str):
        self.UserAccessToken = UserAccessToken


    def UserCartList(self):
        """
        İlgili Kullanıcıya ait sepeteki tüm ürünleri çekme
        """
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        data = dict(
            Token=self.UserAccessToken
        )
        url = f'{settings_api["usersepet"]}'
        data = json.dumps(data)
        r = requests.get(url=url, data=data, headers=headers)
        if r.status_code == 200:
            return r.json()
        return False

    def UserCartDeleteProduct(self, pid: int):
        """
        İlgili kullanıcının sepetinden ürünü silme.
        """
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        data = dict(
            Token=self.UserAccessToken
        )
        params = {"p": pid}
        url = f'{settings_api["usersepet"]}'
        data = json.dumps(data)
        r = requests.delete(url=url, data=data, headers=headers, params=params)
        if r.status_code == 204:
            return True
        return False


    def addCart(self, UrunId: int, UrunADET: int):
        """
        Ilgili ürünü ilgili acccess token a sahip kullanıcının sepetine ekleme.   
        """
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        data = dict(
            Urun=UrunId,
            UrunADET=UrunADET,
            Token=self.UserAccessToken
        )
        url = f'{settings_api["usersepet"]}'
        data = json.dumps(data)
        r = requests.post(url=url, data=data, headers=headers)
        if r.status_code == 201:
            return True
        return False


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class UyeAccControl:
    """
    Kullanıcının sepet onaylamak için gerekli bakiye kontrolerinin yapıldığı / Adres bilgilerinin çekildeiği class
    """
    def __init__(self, DiscordID: int, totalfee):
        self.DiscordID = DiscordID
        self.totalfee = totalfee
    

    def WalletControlAndAddresses(self):
        """
        Kullanıcı DiscordID ile sistemden API ile sanal cüzdan bakiyesini kontorol et
        eğer toplam sepet tutarını ödeyebilecek kadar bakiyeye varsa kullanıcının adres bilgilerini respons da gönder(code 200)
        eğer yeterli bakiye yoksa responsa da "islem": { "message": "Sanal cüzdanda yeterli miktarda bakiye yok!" } gönder.
        """
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        data = dict(
            totalfee=self.totalfee
        )
        url = f'{settings_api_deci["UyeAccControl"]}{self.DiscordID}/'
        data = json.dumps(data, cls=DecimalEncoder)
        r = requests.get(url=url, data=data, headers=headers)
        if r.status_code == 200:
            return r.json()
        return False




class UyeSiparis:
    """
    Kullanıcı sipariş verme, geçmiş siparişleri listeleme ve sipariş güncelleme(iptal etme) gibi işlemlerin
    yapıldığı class.
    """

    def __init__(self, UserAccessToken: str, DiscordId: int):
        self.UserAccessToken = UserAccessToken
        self.DiscordId = DiscordId


    def Checkout(self, SepetToplam: Decimal, userWALLET: str, **address):
        """
        Kullanıcı sipariş verme.
        """
        ecommerceDict = dict(
            userWALLET = userWALLET,
            **address,
            Token = self.UserAccessToken
        )
        """
        {
           "userWALLET": 999999999.00, 
            "ADRES": "Mahale / sokak / kapı no/ Ülke / şehir / ilçe",
            "ADRESBASLIK": "test ADRESBASLIK",
            "ADRESALICI": "test ADRESALICI",
            "ADRESALICIGSM": "test ADRESALICIGSM",
            "ADRESALICITC": "test ADRESALICITC",
           "Token": "rfr"
        }
        
        """

        deciDict = dict(
            Firma=settings_api_deci["FirmaID"],
            WalletLogAmount=str(SepetToplam),
            DiscordId=self.DiscordId
        )

        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }

        ecommerce_url = f'{settings_api["usersiparis"]}'
        ecommerce_data = json.dumps(ecommerceDict)
        r_ecommerce = requests.post(url=ecommerce_url, data=ecommerce_data, headers=headers)

        deci_url = f'{settings_api_deci["logs"]}'
        deci_data = json.dumps(deciDict)
        r_deci = requests.post(url=deci_url, data=deci_data, headers=headers)
        return r_deci.status_code == 201 and r_ecommerce.status_code == 201


    def get_All_Siparis(self):
        """
        Tüm geçmiş siparişleri tarihe göre listele.
         GET
         {
            "Token": ""
         }

        """
        pass


    def SiparisUpdate_or_cancel(self):
        """
        Sipariş güncelleme(iptal etme)
        PUT
         {
             "SiparisID": 1,
             "SiparisADRES": "adress",
             "SiparisADET": 2,
             "SiparisFIYAT": "25499.00",
             "User": 4,
             "Urun": 2171,
            "Token": ""
         }

        """
        pass


