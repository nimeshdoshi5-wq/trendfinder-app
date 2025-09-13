import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import plotly.express as px

# =========================
# 🔑 Secrets (from Streamlit Cloud)
# =========================
CONSUMER_KEY = st.secrets["CONSUMER_KEY"]
CONSUMER_SECRET = st.secrets["CONSUMER_SECRET"]

# =========================
# 🔐 Access Token Function
# =========================
def get_access_token():
    url = "https://napi.kotaksecurities.com/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CONSUMER_KEY,
        "client_secret": CONSUMER_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error(f"❌ Token Error: {response.text}")
        return None

ACCESS_TOKEN = get_access_token()

# =========================
# 📊 Indicators
# =========================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_vwap(df):
    return (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()

# =========================
# 📥 Fetch Stock Data
# (Kotak Neo API endpoint को अपने हिसाब से adjust करो)
# =========================
def fetch_stock_data(symbol):
    url = f"https://napi.kotaksecurities.com/stockdata/{symbol}"  # 🔴 Example endpoint
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    else:
        st.error(f"{symbol}: {response.text}")
        return pd.DataFrame()

# =========================
# 📈 Breakout Conditions
# =========================
def check_conditions(symbol, df):
    df["RSI"] = calculate_rsi(df["Close"])
    df["VWAP"] = calculate_vwap(df)

    latest = df.iloc[-1]
    avg_vol = df["Volume"].tail(10).mean()
    prev_high = df["High"].rolling(10).max().iloc[-2]
    prev_low = df["Low"].rolling(10).min().iloc[-2]

    result = None

    # ✅ Upside condition
    if (
        latest["Close"] > prev_high
        and latest["Close"] > latest["VWAP"]
        and latest["RSI"] > 60
        and latest["Volume"] > avg_vol
    ):
        result = {
            "Symbol": symbol,
            "Close": latest["Close"],
            "RSI": latest["RSI"],
            "Volume": latest["Volume"],
            "Signal": "UP"
        }

    # 🔻 Downside condition
    elif (
        latest["Close"] < prev_low
        and latest["Close"] < latest["VWAP"]
        and latest["RSI"] < 40
        and latest["Volume"] > avg_vol
    ):
        result = {
            "Symbol": symbol,
            "Close": latest["Close"],
            "RSI": latest["RSI"],
            "Volume": latest["Volume"],
            "Signal": "DOWN"
        }

    return result

# =========================
# 🚀 Streamlit App
# =========================
st.set_page_config(page_title="TrendFinder Pro+ - Breakout Scanner", layout="wide")
st.title("📈 TrendFinder Pro+ - Breakout Scanner (F&O + Indices)")

if not ACCESS_TOKEN:
    st.stop()

symbols = ["RELIANCE", "TCS", "INFY", "ICICIBANK"]  # 🔴 Example list (F&O + Nifty50 डालना होगा)

results = []
for symbol in symbols:
    df = fetch_stock_data(symbol)
    if not df.empty:
        res = check_conditions(symbol, df)
        if res:
            results.append(res)

if results:
    df_results = pd.DataFrame(results)
    for idx, row in df_results.iterrows():
        if row["Signal"] == "UP":
            st.markdown(f"🟢 **{row['Symbol']}** ↑ (Close: {row['Close']}, RSI: {row['RSI']:.2f})")
        else:
            st.markdown(f"🔴 **{row['Symbol']}** ↓ (Close: {row['Close']}, RSI: {row['RSI']:.2f})")

    st.dataframe(df_results, use_container_width=True)
else:
    st.info("⏰ Market Closed or No breakout stocks right now. Showing last available data.")
