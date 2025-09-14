import streamlit as st
import requests

st.title("Kotak Neo API - Step 1 Login (TOTP)")

# User Input
mobile_number = st.text_input("Mobile Number (with +91)", "+917016250766")
totp_code = st.text_input("TOTP Code (6-digit from Neo app)", "1225")
access_token = st.text_area("Access Token (2bd863ac-8a0c-45b6-8752-209b88850f0d)")

if st.button("Login with TOTP"):
    # Headers
    headers = {
        "Authorization": f"Bearer {access_token}",  # Correct format
        "Content-Type": "application/json",
        "neo-fin-key": "neotradeapi"
    }

    # Request Body
    payload = {
        "mobileNumber": mobile_number,
        "totp": totp_code
    }

    # POST Request
    try:
        response = requests.post(
            "https://gw-napi.kotaksecurities.com/login/1.0/login/v6/totp/login",
            headers=headers,
            json=payload
        )
        data = response.json()
        st.write("Status Code:", response.status_code)
        st.json(data)
        
        # Optional: Extract sid & view token if success
        if response.status_code == 200 and "data" in data:
            st.success("Login Successful!")
            st.write("SID:", data["data"].get("sid"))
            st.write("View Token:", data["data"].get("token"))

    except Exception as e:
        st.error(f"Error: {e}")
