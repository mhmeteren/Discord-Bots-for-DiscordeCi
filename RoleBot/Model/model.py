import requests
from Model.functions import *

class UyeDeadAcc:

    DeadList = []
    FirmaID = int
    def __init__(self):
        self.FirmaID = settings["FirmaID"]

    def getDeadList(self):
        r = requests.get(f'{settings_api["DeadUser"]}/{self.FirmaID}')
        if r.status_code == 200:   
            self.DeadList = r.json()

    def DeleteDeadList(self):
            r = requests.delete(f'{settings_api["DeadUser"]}/{self.FirmaID}')
            return r.status_code == 200
            

class UyeAccPerm:

    DiscordList = []
    FirmaID = int
    def __init__(self):
        self.FirmaID = settings["FirmaID"]
    
    def getDiscordList(self):
        r = requests.get(f'{settings_api["UyeAccPerm"]}/{self.FirmaID}')
        if r.status_code == 200:
            for dc in  r.json():   
                self.DiscordList.append(dc["DiscordID"])
            return True
        return False
         