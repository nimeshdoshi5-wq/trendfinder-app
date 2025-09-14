import streamlit as st
from libs.neo_api_client.session import NeoSession

st.title("Kotak Neo Trend Finder - Login Test")

# User Inputs
userid = st.text_input("User ID / Client ID")
consumer_key = st.text_input("Consumer Key")
consumer_secret = st.text_input("Consumer Secret")
totp_secret = st.text_input("TOTP Secret (base32)")

if st.button("Login"):
    try:
        session = NeoSession(consumer_key, consumer_secret)
        token = session.login_with_totp(userid, totp_secret)
        st.success(f"✅ Login Successful! Session Token: {token}")
    except Exception as e:
        st.error(f"❌ Login Failed: {str(e)}")
