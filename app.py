# Kotak Neo Trend Finder - Login Test with Pre-Filled Values

import streamlit as st
import pyotp
import requests
import time

# -----------------------------
# Default Values (तेरे details से भरे हुए)
# -----------------------------
DEFAULT_USER_ID = "XUBPA"   # यहां तेरा Client ID डाल
DEFAULT_CONSUMER_KEY = "umPAhnWbqVMDMKbN0UfUr4zmq7ka"
DEFAULT_CONSUMER_SECRET = "zk2xX_rLFWuuy7X1wFVsUTHok28a"
DEFAULT_TOTP_SECRET = "4649"  # यहां वो secret डाल जो Neo App से मिलता है

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Kotak Neo Trend Finder - Login Test")

user_id = st.text_input("User ID / Client ID", value=DEFAULT_USER_ID)
consumer_key = st.text_input("Consumer Key", value=DEFAULT_CONSUMER_KEY)
consumer_secret = st.text_input("Consumer Secret", value=DEFAULT_CONSUMER_SECRET)
totp_secret = st.text_input("TOTP Secret (base32)", value=DEFAULT_TOTP_SECRET)

if st.button("Login Test"):
    try:
        # OTP Generate
        totp = pyotp.TOTP(totp_secret)
        otp = totp.now()

        st.write(f"Generated OTP: {otp}")

        # Login API call
        url = "https://napi.kotaksecurities.com/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "password",
            "username": user_id,
            "password": otp,
            "client_id": consumer_key,
            "client_secret": consumer_secret
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            token = response.json().get("access_token", "")
            st.success("✅ Login Successful!")
            st.code(token, language="text")
        else:
            st.error(f"❌ Login Failed! {response.status_code}")
            st.json(response.json())

    except Exception as e:
        st.error(f"Error: {e}")
