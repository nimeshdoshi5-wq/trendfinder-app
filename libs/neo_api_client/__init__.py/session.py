
import requests

class NeoSession:
    def __init__(self, base_url, api_token, client_key):
        self.base_url = base_url
        self.api_token = api_token
        self.client_key = client_key

    def login_totp(self, mobile, ucc, totp):
        url = f"{self.base_url}/login/1.0/login/v6/totp/login"
        headers = {
            "Authorization": self.api_token,
            "neo-fin-key": self.client_key,
            "Content-Type": "application/json"
        }
        payload = {
            "mobileNumber": mobile,
            "ucc": ucc,
            "totp": totp
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, response.text
