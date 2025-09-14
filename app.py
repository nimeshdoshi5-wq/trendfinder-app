import streamlit as st
from libs.neo_api_client.session import NeoSession

st.title("Trend Finder - Dummy Test")

# Test button
if st.button("Run Test"):
    session = NeoSession("https://gwapi.kotaksecurities.com")
    resp = session.login_dummy("XUBPA", "123456")
    st.write("Login Response:", resp)
