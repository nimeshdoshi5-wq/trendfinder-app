import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import plotly.express as px

# =========================
# 🔑 Neo Access Token (manual)
# =========================
ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]
BASE_URL = "https://napi.kotaksecurities.com"

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
# Endpoint को Neo docs के हिसाब से adjust करो
# =========================
def fetch_stock_data(symbol):
    url = f"{BASE_URL}/stockdata/{symbol}"  # 🔴 Adjust this endpoint
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
        return df
    else:
        st.error(f"{symbol}: {response.status_code} {response.text}")
        return pd.DataFrame()

# =========================
# 📈 Breakout Conditions
# =========================
def check_conditions(symbol, df):
    if df.empty or len(df) < 10:
        return None
    df["RSI"] = calculate_rsi(df["Close"])
    df["VWAP"] = calculate_vwap(df)
    latest = df.iloc[-1]
    avg_vol = df["Volume"].tail(10).mean()
    prev_high = df["High"].rolling(10).max().iloc[-2]
    prev_low = df["Low"].rolling(10).min().iloc[-2]

    result = None

    # ✅ Upside condition
    if latest["Close"] > prev_high and latest["Close"] > latest["VWAP"] and latest["RSI"] > 60 and latest["Volume"] > avg_vol:
        result = {"Symbol": symbol, "Close": latest["Close"], "RSI": latest["RSI"], "Volume": latest["Volume"], "Signal": "UP"}

    # 🔻 Downside condition
    elif latest["Close"] < prev_low and latest["Close"] < latest["VWAP"] and latest["RSI"] < 40 and latest["Volume"] > avg_vol:
        result = {"Symbol": symbol, "Close": latest["Close"], "RSI": latest["RSI"], "Volume": latest["Volume"], "Signal": "DOWN"}

    return result

# =========================
# 🚀 Streamlit App
# =========================
st.set_page_config(page_title="TrendFinder Pro+ - Breakout Scanner", layout="wide")
st.title("📈 TrendFinder Pro+ - Breakout Scanner (F&O + Indices)")

# Symbols (example: Nifty50, BankNifty, Futures)
symbols = ["RELIANCE", "TCS", "INFY", "ICICIBANK", "NIFTY", "BANKNIFTY"]  # 🔴 Add all F&O symbols here

results = []
for symbol in symbols:
    df = fetch_stock_data(symbol)
    res = check_conditions(symbol, df)
    if res:
        results.append(res)

if results:
    df_results = pd.DataFrame(results)
    # Sector-wise sorting (example)
    df_results = df_results.sort_values(by="Signal", ascending=False)

    for idx, row in df_results.iterrows():
        if row["Signal"] == "UP":
            st.markdown(f"🟢 **{row['Symbol']}** ↑ (Close: {row['Close']}, RSI: {row['RSI']:.2f})")
        else:
            st.markdown(f"🔴 **{row['Symbol']}** ↓ (Close: {row['Close']}, RSI: {row['RSI']:.2f})")

    st.dataframe(df_results, use_container_width=True)
else:
    st.info("⏰ Market Closed or No breakout stocks currently. Showing last available data.")
