import requests
import json
from Models.functions import settings_api


class Product:
    """
    Kullanıcılara bildirim olarak gönderilicek ürünleri API ile cekmek.
    """
    def __init__(self, page: int, page_size: int):
        self.page = page
        self.page_size = page_size


    def createProductPutList(self):
        """
        Çekilen ürünlerin daha sonra çekildilerinin(Kullanıcıya sunulup sunulmadığının) belirlenmesi için 
        UrunDURUM ları False yapılarak tekrar ilgili url le PUT isteğinde bulunulucak.
        """
        temp = []
        for p in self.productList["results"]:
            temp.append(
                dict(
                    OuID=p["OuID"],
                    UrunDURUM=False
                )
            )

        self.ProductPutList = temp
    

    def getProducts(self):
        """
        Ürünlerin API ile çekilmesi
        """
        params = {'page': self.page, 'page_size': self.page_size}
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        r = requests.get(f'{settings_api["pnoti"]}', params=params, headers=headers)
        if r.status_code == 200:
            self.productList = r.json()
            self.createProductPutList()
            return True
        return False
    

    def setProducs(self):
        """
        Önerilen ürünlerin tekrar önerilmemesi için UrunDURUM false yapılarak PUT isteği yapılıyor.
        """
        headers = {
            'content-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'application/json'
        }
        data = json.dumps(
            dict(
                OnerilenUrunler=self.ProductPutList
            )
        )
        r = requests.put(f'{settings_api["pnoti"]}', data=data, headers=headers)
        if r.status_code == 200:
            return True
        return False
    
