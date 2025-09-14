# app.py
import streamlit as st
import requests

st.title("Kotak Neo API Login Test")

# User inputs
user_id = st.text_input("User ID / Client ID")
consumer_key = st.text_input("Consumer Key")
consumer_secret = st.text_input("Consumer Secret")
otp_code = st.text_input("TOTP / OTP from Neo App", max_chars=6)

if st.button("Login"):
    if not user_id or not consumer_key or not consumer_secret or not otp_code:
        st.error("Please fill all fields")
    else:
        # Login API endpoint
        login_url = "https://gw-napi.kotaksecurities.com/login/1.0"

        # Headers
        headers = {
            "Content-Type": "application/json",
            "X-ClientCode": user_id,
            "X-ConsumerKey": consumer_key,
            "X-ConsumerSecret": consumer_secret
        }

        # Payload
        payload = {
            "otp": otp_code
        }

        try:
            response = requests.post(login_url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                st.success("Login Successful!")
                st.json(data)  # Shows full response including access token
            else:
                st.error(f"Login failed! Status Code: {response.status_code}")
                st.json(response.json())
        except Exception as e:
            st.error(f"Error: {e}")
