import streamlit as st
import requests

st.title("Kotak Neo API - Step 1 Login (TOTP)")

# User Inputs
mobile_number = st.text_input(" (+917016250766):")
totp_code = st.text_input("1225:")
access_token = st.text_input("eyJ4NXQiOiJNbUprWWpVMlpETmpNelpqTURBM05UZ3pObUUxTm1NNU1qTXpNR1kyWm1OaFpHUTFNakE1TmciLCJraWQiOiJaalJqTUdRek9URmhPV1EwTm1WallXWTNZemRtWkdOa1pUUmpaVEUxTlRnMFkyWTBZVEUyTlRCaVlURTRNak5tWkRVeE5qZ3pPVGM0TWpGbFkyWXpOUV9SUzI1NiIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJjbGllbnQ0NzIzOSIsImF1dCI6IkFQUExJQ0FUSU9OIiwiYXVkIjoidW1QQWhuV2JxVk1ETUtiTjBVZlVyNHptcTdrYSIsIm5iZiI6MTc1Nzc4MDAyOCwiYXpwIjoidW1QQWhuV2JxVk1ETUtiTjBVZlVyNHptcTdrYSIsInNjb3BlIjoiZGVmYXVsdCIsImlzcyI6Imh0dHBzOlwvXC9uYXBpLmtvdGFrc2VjdXJpdGllcy5jb206NDQzXC9vYXV0aDJcL3Rva2VuIiwiZXhwIjozNjAwMTc1Nzc4MDAyOCwiaWF0IjoxNzU3NzgwMDI4LCJqdGkiOiIyNTdmMTM5Mi04NzhhLTQzODctODdjZS1hY2EyMzZkMGVlYjMifQ.IDSFdzt7u1sM1weh4gk13u3SovYMHLZiN-WBD4bo0WnGmN2rqhB8bbn5WwjYYpwvdaesB0p090ZYwOzNXW1_6wBIqtS8tv9ZENW5c6-cV5zCsV4Sqb2MosDhXt4wuILttTndY7a8JkAqCw8NaoFdaEiAb1sKSEPBEARZkBjq9BidH2jlzQA1KYqbPX4ZeSYmQzX-2WGnClDGXoJ03bVAsYC4CKR28yBRMpteOlKonURT7-hm7hZEwq1z-unZ1HEpaK2g5D2Mobs-3EUDRAVvz8ioAaDiXuIytK35L4VXtm885-1inC_aIHuhwiaHzOZuIe7fvb4Uxveo0W4ZZ4E9EQ:")

if st.button("Login with TOTP"):
    url = "https://gw-napi.kotaksecurities.com/login/1.0/login/v6/totp/login"
    
    headers = {
        "Authorization": access_token,       # yahi Access Token use hoga
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json"
    }
    
    payload = {
        "mobileNumber": mobile_number,
        "totp": totp_code
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    st.write("Status Code:", response.status_code)
    
    try:
        json_data = response.json()
        st.json(json_data)  # Pure response JSON display
        if "data" in json_data:
            st.success("Login Successful! ✅")
            st.write("View Token:", json_data["data"].get("token"))
            st.write("Session ID (sid):", json_data["data"].get("sid"))
        else:
            st.error("Login failed. Check mobile/TOTP/Access Token.")
    except Exception as e:
        st.error("Error parsing response:", e)
