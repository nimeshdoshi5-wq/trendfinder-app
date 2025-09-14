import streamlit as st
import requests

st.title("Kotak Neo API - Step 1 Login (TOTP)")

# User Input
mobile_number = st.text_input("Mobile Number (with +91)", "+917016250766")
totp_code = st.text_input("TOTP Code (6-digit from Neo app)", "1225")
access_token = st.text_area("Access Token (eyJ4NXQiOiJNbUprWWpVMlpETmpNelpqTURBM05UZ3pObUUxTm1NNU1qTXpNR1kyWm1OaFpHUTFNakE1TmciLCJraWQiOiJaalJqTUdRek9URmhPV1EwTm1WallXWTNZemRtWkdOa1pUUmpaVEUxTlRnMFkyWTBZVEUyTlRCaVlURTRNak5tWkRVeE5qZ3pPVGM0TWpGbFkyWXpOUV9SUzI1NiIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJjbGllbnQ0NzIzOSIsImF1dCI6IkFQUExJQ0FUSU9OIiwiYXVkIjoidW1QQWhuV2JxVk1ETUtiTjBVZlVyNHptcTdrYSIsIm5iZiI6MTc1Nzc4MDAyOCwiYXpwIjoidW1QQWhuV2JxVk1ETUtiTjBVZlVyNHptcTdrYSIsInNjb3BlIjoiZGVmYXVsdCIsImlzcyI6Imh0dHBzOlwvXC9uYXBpLmtvdGFrc2VjdXJpdGllcy5jb206NDQzXC9vYXV0aDJcL3Rva2VuIiwiZXhwIjozNjAwMTc1Nzc4MDAyOCwiaWF0IjoxNzU3NzgwMDI4LCJqdGkiOiIyNTdmMTM5Mi04NzhhLTQzODctODdjZS1hY2EyMzZkMGVlYjMifQ.IDSFdzt7u1sM1weh4gk13u3SovYMHLZiN-WBD4bo0WnGmN2rqhB8bbn5WwjYYpwvdaesB0p090ZYwOzNXW1_6wBIqtS8tv9ZENW5c6-cV5zCsV4Sqb2MosDhXt4wuILttTndY7a8JkAqCw8NaoFdaEiAb1sKSEPBEARZkBjq9BidH2jlzQA1KYqbPX4ZeSYmQzX-2WGnClDGXoJ03bVAsYC4CKR28yBRMpteOlKonURT7-hm7hZEwq1z-unZ1HEpaK2g5D2Mobs-3EUDRAVvz8ioAaDiXuIytK35L4VXtm885-1inC_aIHuhwiaHzOZuIe7fvb4Uxveo0W4ZZ4E9EQ)")

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
