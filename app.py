# Kotak Neo API Trend Finder - Python Template
# Requirements: neo_api_client (Kotak Neo Python SDK), requests

import neo_api_client
import time

# -------------------------------
# Step 1: Initialize Base URL & Session
# -------------------------------
client = neo_api_client.BaseUrl()
session = neo_api_client.SessionINIT(client)

# -------------------------------
# Step 2: TOTP Login
# -------------------------------
mobile_number = "+917016250766"  # Tumhara mobile number
totp_code = "1225"  # Neo app se jo 6-digit code aata hai, login ke waqt update karna hoga

# Step 2a: Initiate TOTP login
login_resp = neo_api_client.Totp_login(session, mobile_number)
print("TOTP Login initiated:", login_resp)

# Step 2b: Validate TOTP
validation_resp = neo_api_client.Totp_validation(session, totp_code)
print("TOTP Validation Response:", validation_resp)

# -------------------------------
# Step 3: Use Session to Fetch Quotes
# -------------------------------
scrip_code = "TCS"  # Example: TCS stock
quote_resp = neo_api_client.quotes(session, scrip_code)
print("Quote for", scrip_code, ":", quote_resp)

# -------------------------------
# Step 4: Place Order Example (Optional)
# -------------------------------
# order_data = {
#     "exchange": "NSE",
#     "tradingsymbol": "TCS",
#     "transactiontype": "BUY",
#     "quantity": 1,
#     "ordertype": "MARKET",
#     "producttype": "INTRADAY"
# }
# place_order_resp = neo_api_client.placeorder(session, order_data)
# print("Place Order Response:", place_order_resp)
