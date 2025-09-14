# app.py

import streamlit as st
from libs.neo_api_client.session import NeoSession

# --- Config ---
BASE_URL = "https://gwapi.kotaksecurities.com"
API_TOKEN = "2bd863ac-8a0c-45b6-8752-209b88850f0d"
NEO_CLIENT_KEY = "neotradeapi"

st.title("Kotak Neo Trend Finder - Simple Login")

# User inputs
ucc = st.text_input("Client Code / UCC")
totp = st.text_input("TOTP (6 digits)", max_chars=6, type="password")

if st.button("Login"):
    if not ucc or not totp:
        st.error("Please enter both UCC and TOTP.")
    else:
        session = NeoSession(BASE_URL, API_TOKEN, NEO_CLIENT_KEY)
        success, resp = session.login_totp(ucc, totp)
        if success:
            st.success(f"Login Successful!\nSID: {session.sid}")
            st.json(resp)
        else:
            st.error("Login Failed. Check UCC/TOTP or connection.")
