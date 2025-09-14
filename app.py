import streamlit as st
from libs.neo_api_client.session import NeoSession

st.title("Kotak Neo Trend Finder - Login Test")

base_url = st.text_input("Base URL", "https://gwapi.kotaksecurities.com")
api_token = st.text_input("API Token (from NEO dashboard)")
client_key = st.text_input("Neo Client Key", "neotradeapi")
mobile = st.text_input("Mobile Number (+91...)")
ucc = st.text_input("Client ID / UCC")
totp = st.text_input("TOTP (6 digits)")
mpin = st.text_input("MPIN (6 digits)", type="password")

if st.button("Login with TOTP"):
    session = NeoSession(base_url, api_token, client_key)
    success, resp = session.login_totp(mobile, ucc, totp)
    if success:
        st.success("Step 1 Successful! Session created.")
        st.json(resp)
    else:
        st.error("Step 1 Failed")
        st.json(resp)

if st.button("Validate MPIN"):
    if "session" not in locals():
        st.error("Step 1 first!")
    else:
        success, resp = session.validate_mpin(mpin)
        if success:
            st.success("Step 2 Successful! Trade token received.")
            st.json(resp)
        else:
            st.error("Step 2 Failed")
            st.json(resp)
