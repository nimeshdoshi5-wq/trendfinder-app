# trendfinder_app.py
import streamlit as st
import requests
import json

st.set_page_config(page_title="Kotak Neo Trend Finder", layout="wide")
st.title("Kotak Neo Trend Finder App")

# -----------------------
# Step 1: Inputs
# -----------------------
st.sidebar.header("API Settings")
consumer_key = st.sidebar.text_input("Consumer Key", value="umPAhnWbqVMDMKbN0UfUr4zmq7ka")
consumer_secret = st.sidebar.text_input("Consumer Secret", value="zk2xX_rLFWuuy7X1wFVsUTHok28a")
access_token = st.sidebar.text_input("Access Token", value="2bd863ac-8a0c-45b6-8752-209b88850f0d", type="password")

st.sidebar.markdown("""
> ⚠️ Update Access Token after expiry.  
> You don’t need to enter TOTP every time.
""")

# -----------------------
# Step 2: API Selection
# -----------------------
api_options = {
    "Quotes": "https://gw-napi.kotaksecurities.com/apim/quotes/1.0",
    "Orders": "https://gw-napi.kotaksecurities.com/Orders/2.0"
}
selected_api = st.selectbox("Select API Endpoint", list(api_options.keys()))

# -----------------------
# Step 3: Make API Call
# -----------------------
if st.button("Call API"):
    if access_token.strip() == "":
        st.error("Please enter your Access Token!")
    else:
        headers = {
            "Authorization": f"Bearer {access_token.strip()}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(api_options[selected_api], headers=headers)
            if response.status_code == 200:
                st.success("API Call Successful!")
                st.json(response.json())
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

# -----------------------
# Step 4: Real-time Display Placeholder
# -----------------------
st.markdown("---")
st.subheader("Real-time Data (Optional)")

if st.button("Fetch Latest Quote for TCS"):
    symbol = "TCS"
    quote_endpoint = f"https://gw-napi.kotaksecurities.com/apim/quotes/1.0/{symbol}"
    try:
        response = requests.get(quote_endpoint, headers={"Authorization": f"Bearer {access_token.strip()}"})
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")
