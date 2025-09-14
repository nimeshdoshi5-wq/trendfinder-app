import requests

class NeoSession:
    def __init__(self, base_url, api_token, client_key):
        self.base_url = base_url
        self.api_token = api_token          # Authorization token from Neo dashboard
        self.client_key = client_key        # neo-fin-key
        self.sid = None                     # Session ID from Step 1
        self.view_token = None              # View token from Step 1
        self.trade_token = None             # Trade token from Step 2

    def login_totp(self, mobile_number, ucc, totp):
        url = f"{self.base_url}/login/1.0/login/v6/totp/login"
        headers = {
            "Authorization": self.api_token,
            "neo-fin-key": self.client_key,
            "Content-Type": "application/json"
        }
        payload = {
            "mobileNumber": mobile_number,
            "ucc": ucc,
            "totp": totp
        }
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if response.status_code == 200 and "data" in data:
            self.sid = data["data"]["sid"]
            self.view_token = data["data"]["token"]
            return True, data
        else:
            return False, data

    def validate_mpin(self, mpin):
        url = f"{self.base_url}/login/1.0/login/v6/totp/validate"
        headers = {
            "Authorization": self.api_token,
            "neo-fin-key": self.client_key,
            "Content-Type": "application/json",
            "sid": self.sid,
            "Auth": self.view_token
        }
        payload = {"mpin": mpin}
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if response.status_code == 200 and "data" in data:
            self.trade_token = data["data"]["token"]
            return True, data
        else:
            return False, data
