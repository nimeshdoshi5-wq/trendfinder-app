
import requests
import pyotp

class NeoSession:
    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_url = "https://napi.kotaksecurities.com"  # Kotak Neo API Base URL
        self.session_token = None

    def login_with_totp(self, userid, totp_secret):
        """
        userid: Kotak Neo user id / client id
        totp_secret: Neo app से निकला हुआ secret (base32 format)
        """
        # हर बार नया 6-digit TOTP code generate होगा
        totp = pyotp.TOTP(totp_secret).now()
        url = f"{self.base_url}/login/1.0"

        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        payload = {
            "userid": userid,
            "consumerKey": self.consumer_key,
            "consumerSecret": self.consumer_secret,
            "totp": totp
        }

        # API Call
        res = requests.post(url, json=payload, headers=headers)

        if res.status_code == 200:
            data = res.json()
            # session token निकालना
            self.session_token = data.get("data", {}).get("sessionToken")
            return self.session_token
        else:
            raise Exception(f"Login failed: {res.status_code} {res.text}")
