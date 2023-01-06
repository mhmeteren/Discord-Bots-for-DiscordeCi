import requests
from models.functions import settings_api


class DiscordAcc:
    def __init__(self, DiscordID):
        self.DiscordID = DiscordID


    def DiscordAccControl(self, token):
        r = requests.get(f'{settings_api["DiscordAcc"]}{self.DiscordID}')

        if (r.status_code == 200):
            _token = r.json()["TOKEN"]
            UyeID = r.json()["UyeID"]

            if _token == str(token):
                r2 = requests.put(f'{settings_api["DiscordAcc"]}{self.DiscordID}', data={'TOKENDURUM': True})
                r3 = requests.put(f'{settings_api["User"]}{UyeID}', data={"DiscordID": self.DiscordID})
                return (r2.status_code == 200) and (r3.status_code == 201)
        return False