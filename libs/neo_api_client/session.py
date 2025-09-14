# libs/neo_api_client/session.py

import requests

class NeoSession:
    def __init__(self, base_url, api_token, neo_client_key):
        self.base_url = base_url
        self.api_token = api_token
        self.neo_client_key = neo_client_key
        self.sid = None
        self.view_token = None
        self.trade_token = None

    def login_totp(self, ucc, totp):
        """
        Login using only Client ID / UCC and TOTP
        """
        url = f"{self.base_url}/login/1.0/login/v6/totp/login"
        headers = {
            "Authorization": self.api_token,
            "neo-fin-key": self.neo_client_key,
            "Content-Type": "application/json"
        }
        payload = {
            "ucc": ucc,
            "totp": totp
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            print("Login Response:", data)
            if "data" in data:
                self.sid = data["data"].get("sid")
                self.view_token = data["data"].get("token")
                return True, data
            else:
                return False, data
        except requests.exceptions.RequestException as e:
            print("Login Error:", e)
            return False, None

# ===== Usage Example =====
if __name__ == "__main__":
    base_url = "https://gwapi.kotaksecurities.com"
    api_token = "2bd863ac-8a0c-45b6-8752-209b88850f0d"
    neo_client_key = "neotradeapi"
    ucc = "xubpa"
    totp = "144008"   # 6-digit TOTP from authenticator

    session = NeoSession(base_url, api_token, neo_client_key)
    success, resp = session.login_totp(ucc, totp)
    if success:
        print("Login Successful! SID:", session.sid)
    else:
        print("Login Failed.")
