import streamlit as st
import requests

st.title("Kotak Neo API Login")

# User inputs
mobile_number = st.text_input("Mobile Number (with +91)", "+917016250766")
totp_code = st.text_input("TOTP Code (6-digit from Neo app)", "0223")
access_token = "2bd863ac-8a0c-45b6-8752-209b88850f0d"  # Fixed Access Token
neo_fin_key = "umPAhnWbqVMDMKbN0UfUr4zmq7ka"  # Your Consumer Key

if st.button("Login"):
    try:
        # Step 1: Login with TOTP
        url = "https://gw-napi.kotaksecurities.com/login/1.0/login/v6/totp/login"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "neo-fin-key": neo_fin_key,
            "Content-Type": "application/json"
        }
        payload = {
            "mobileNumber": mobile_number,
            "totp": totp_code
        }
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.status_code == 200 and "data" in data:
            sid = data["data"]["sid"]
            view_token = data["data"]["token"]
            st.success(f"Login successful!\nSID: {sid}\nView Token: {view_token}")
        else:
            st.error(f"Login failed!\nResponse: {data}")
    except Exception as e:
        st.error(f"Error occurred: {e}")
