import requests
import pyotp

class NeoSession:
    def __init__(self, user_id, consumer_key, consumer_secret, totp_secret):
        self.user_id = user_id
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.totp_secret = totp_secret
        self.session_token = None

    def get_otp(self):
        """
        Auto-generate TOTP code from secret (valid for ~30 sec)
        """
        secret = self.totp_secret.strip()
        # Fix base32 padding issue
        missing_padding = len(secret) % 8
        if missing_padding != 0:
            secret += "=" * (8 - missing_padding)
        return pyotp.TOTP(secret).now()

    def login(self):
        """
        Login to Kotak Neo using Consumer Key, Secret, UserID and TOTP
        """
        otp = self.get_otp()
        payload = {
            "userid": self.user_id,
            "consumerKey": self.consumer_key,
            "consumerSecret": self.consumer_secret,
            "totp": otp
        }

        url = "https://wso2.kotaksecurities.com/neo/login/1.0"  # official login endpoint
        res = requests.post(url, json=payload)

        if res.status_code == 200:
            try:
                data = res.json()
                self.session_token = data.get("sessionToken")
                return self.session_token
            except Exception as e:
                raise Exception(f"Login response parse error: {res.text}") from e
        else:
            raise Exception(f"Login failed! Status: {res.status_code}, Response: {res.text}")
