import requests
import random
import datetime
import config
from colorama import *


def output(text, input_color='GREEN'):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = getattr(Fore, input_color.upper())
    print(color + f"[{timestamp}] {text}" + Style.RESET_ALL)

class Vision():
    def __init__(self, proxy):
        self.ip_proxy, self.port_proxy, self.login_proxy, self.password_proxy = proxy.split(':')
        self.folderId = '54afab4f-83d7-4a75-818e-595ba567979d'
        self.headers = {
            'X-Token': config.API_VISION,
            'Content-Type': 'application/json'
        }

    def get_fingerprint(self):
        response = requests.get('https://v1.empr.cloud/api/v1/fingerprints/windows/latest', headers=self.headers)

        fingerprint = response.json()['data']['fingerprint']
        
        fingerprint['webrtc_pref'] = 'off'
        fingerprint['canvas_pref'] = {'noise': round(random.uniform(1.00000000, 1.99999999), 8)}
        fingerprint['webgl_pref'] = {'noise': round(random.uniform(1.00000000, 1.99999999), 8)}
        fingerprint['ports_protection'] = []
        fingerprint['client_rects'] = round(random.uniform(1.000000, 1.999999), 6)

        fingerprint['navigator']['language'] = 'it-IT'
        fingerprint['navigator']['languages'] = ['it-IT', 'it']

        return fingerprint
    
    def create_browser(self):
        url = f'https://v1.empr.cloud/api/v1/folders/{self.folderId}/profiles' 
        body = {
            "profile_name": "youtube",
            "profile_notes": "",
            "profile_tags": [],
            "new_profile_tags": [],
            "profile_status": None,
            "browser": "Chrome",
            "platform": "Windows",
            "fingerprint": self.get_fingerprint()
        }
        response = requests.post(url, headers=self.headers, json=body)
        data = response.json()
        profileId = data['data']['id']
        print(profileId)

        return profileId

    def start_browser(self):
        profileId = self.create_browser()
        print(1)
        body = {
        "args": [],
        "proxy": {
            "type": "socks5",
            "address": str(self.ip_proxy),
            "port": int(self.port_proxy),
            "username": str(self.login_proxy),
            "password": str(self.password_proxy)
        }
        }
        response = requests.post(f'http://127.0.0.1:3030/start/{self.folderId}/{profileId}', headers=self.headers, json=body)
        print(response.text)
        if response.status_code == 200:
            data = response.json()
            port = data['port']


            return port