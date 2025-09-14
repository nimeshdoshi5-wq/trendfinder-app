
from libs.neo_api_client.session import NeoSession

# --- CONFIGURATION ---
BASE_URL = "https://gwapi.kotaksecurities.com"
API_TOKEN = "your-neo-api-token"
CLIENT_KEY = "neotradeapi"
MOBILE = "+91xxxxxxxxxx"
UCC = "your-client-id"
TOTP = "123456"  # Replace with current TOTP from Neo app

# --- LOGIN ---
session = NeoSession(BASE_URL, API_TOKEN, CLIENT_KEY)
success, resp = session.login_totp(MOBILE, UCC, TOTP)

if success:
    print("Login successful!")
    print(resp)
else:
    print("Login failed!")
    print(resp)
