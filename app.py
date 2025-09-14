# kotak_streamlit_app.py
import streamlit as st
import requests
import json

st.set_page_config(page_title="Kotak Neo API - Tread Finder", layout="wide")
st.title("Kotak Neo API - Tread Finder")

# ----------------------
# Step 1: Login Section
# ----------------------
st.header("Step 1: Login with TOTP")

mobile_number = st.text_input("Mobile Number (+91)"917016250766, "")
totp_code = st.text_input("TOTP Code (8999)", "")
access_token = st.text_input(""2bd863ac-8a0c-45b6-8752-209b88850f0d, "")

if st.button("Login"):
    if not mobile_number or not totp_code or not access_token:
        st.error("Sab fields fill karo!")
    else:
        url = "https://gw-napi.kotaksecurities.com/login/1.0/login/v6/totp/login"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "neo-fin-key": "neotradeapi",
            "Content-Type": "application/json"
        }
        payload = {
            "mobileNumber": mobile_number,
            "totp": totp_code
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json().get("data", {})
            st.session_state.sid = data.get("sid")
            st.session_state.view_token = data.get("token")
            st.success("Login Successful!")
            st.write(f"SID: {st.session_state.sid}")
            st.write(f"View Token: {st.session_state.view_token}")
        else:
            st.error(f"Login Failed! {response.text}")

# ----------------------
# Step 2: Place Order
# ----------------------
st.header("Step 2: Place Order")
if "sid" in st.session_state and "view_token" in st.session_state:
    order_symbol = st.text_input("Trading Symbol (e.g. TCS-EQ)", "")
    order_qty = st.number_input("Quantity", min_value=1, step=1)
    order_type = st.selectbox("Order Type", ["L", "MKT", "SL", "SL-M"])
    order_price = st.text_input("Price (0 for market)", "0")
    order_tt = st.selectbox("Buy/Sell", ["B", "S"])

    if st.button("Place Order"):
        place_url = "https://gw-napi.kotaksecurities.com/Orders/2.0/quick/order/rule/ms/place"
        headers = {
            "accept": "application/json",
            "Sid": st.session_state.sid,
            "Auth": st.session_state.view_token,
            "neo-fin-key": "neotradeapi",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        jdata = {
            "am": "NO",
            "dq": "0",
            "es": "nse_cm",
            "mp": "0",
            "pc": "MIS",
            "pf": "N",
            "pr": str(order_price),
            "pt": order_type,
            "qt": str(order_qty),
            "rt": "DAY",
            "tp": "0",
            "ts": order_symbol,
            "tt": order_tt
        }
        response = requests.post(place_url, headers=headers, data={"jData": json.dumps(jdata)})
        if response.status_code == 200:
            st.success("Order Placed Successfully!")
            st.json(response.json())
        else:
            st.error(f"Order Failed! {response.text}")
else:
    st.warning("Login pehle karo")

# ----------------------
# Step 3: View Positions
# ----------------------
st.header("Step 3: View Positions")
if "sid" in st.session_state and "view_token" in st.session_state:
    if st.button("Fetch Positions"):
        pos_url = "https://gw-napi.kotaksecurities.com/Portfolio/1.0/portfolio/v1/positions"
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }
        payload = {"Source": "N"}
        response = requests.post(pos_url, headers=headers, json=payload)
        if response.status_code == 200:
            st.success("Positions Fetched!")
            st.json(response.json())
        else:
            st.error(f"Fetch Failed! {response.text}")
