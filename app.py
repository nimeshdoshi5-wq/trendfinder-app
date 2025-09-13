
CONSUMER_KEY = st.secrets["CONSUMER_KEY"]
CONSUMER_SECRET = st.secrets["CONSUMER_SECRET"]
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
        data = response.json()
        return data["access_token"]
    else:
        st.error(f"Error: {response.text}")
        return None
ACCESS_TOKEN = get_access_token()

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
import pandas as pd

# Auto-refresh every 5 minutes
st_autorefresh(interval=300000, key="refresh")

st.set_page_config(page_title="TrendFinder Pro+ - Kotak NEO", layout="wide")
st.title("📈 TrendFinder Pro+ - Breakout Scanner")

# ---------------------------
# API credentials (use Streamlit Secrets later)
# ---------------------------
CONSUMER_KEY = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"

# ---------------------------
# Get Kotak NEO access token
# ---------------------------
def get_access_token():
    url = "https://api.kotakneo.com/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CONSUMER_KEY,
        "client_secret": CONSUMER_SECRET
    }
    r = requests.post(url, data=payload)
    token_data = r.json()
    return token_data.get("access_token")

ACCESS_TOKEN = get_access_token()
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# ---------------------------
# Symbols input
# ---------------------------
symbols_input = st.sidebar.text_area(
    "Enter Symbols (comma separated):",
    "RELIANCE,TCS,INFY,HDFC,ICICIBANK,NIFTY50,BANKNIFTY,SENSEX"
)
symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]

# ---------------------------
# EMA, VWAP, RSI functions
# ---------------------------
def calculate_ema(df, period=20):
    return df['close'].ewm(span=period).mean()

def calculate_vwap(df):
    return (df['close']*df['volume']).cumsum()/df['volume'].cumsum()

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -1*delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100/(1+rs))
    return rsi

# ---------------------------
# Fetch symbol data from Kotak NEO API
# ---------------------------
def fetch_symbol_data(symbol, interval="5m", days=10):
    url = f"https://api.kotakneo.com/marketdata/intraday/{symbol}?interval={interval}&days={days}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        st.sidebar.warning(f"{symbol}: API Error {r.status_code}")
        return pd.DataFrame()
    data = r.json()
    df = pd.DataFrame(data)
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df

# ---------------------------
# Breakout / Breakdown logic
# ---------------------------
results = []

for symbol in symbols:
    interval = "5m" if symbol not in ["NIFTY50","BANKNIFTY","SENSEX"] else "1d"
    df = fetch_symbol_data(symbol, interval=interval, days=10)
    if df.empty:
        continue

    df["EMA"] = calculate_ema(df, 20)
    df["VWAP"] = calculate_vwap(df)
    df["RSI"] = calculate_rsi(df, 14)

    latest = df.iloc[-1]
    avg_vol = df['volume'].tail(10*78 if interval=="5m" else 10).mean()
    prev_res = df['high'].rolling(10*78 if interval=="5m" else 10).max().iloc[-2]
    prev_sup = df['low'].rolling(10*78 if interval=="5m" else 10).min().iloc[-2]

    beta = 1.2  # Static beta for now

    upside = latest['close']>prev_res and latest['close']>latest['VWAP'] and latest['RSI']>60 and latest['volume']>avg_vol
    downside = latest['close']<prev_sup and latest['close']<latest['VWAP'] and latest['RSI']<40 and latest['volume']>avg_vol

    results.append({
        "Symbol": symbol,
        "Close": round(latest['close'],2),
        "Breakout": "▲" if upside else ("▼" if downside else "-"),
        "EMA": round(latest['EMA'],2),
        "VWAP": round(latest['VWAP'],2),
        "RSI": round(latest['RSI'],2),
        "Beta": beta,
        "Type": "Index" if symbol in ["NIFTY50","BANKNIFTY","SENSEX"] else "Stock"
    })

# ---------------------------
# Display results
# ---------------------------
if results:
    df_res = pd.DataFrame(results)
    st.dataframe(df_res.style.applymap(
        lambda x: 'color: green;' if x=="▲" else ('color: red;' if x=="▼" else ''), subset=["Breakout"]
    ), use_container_width=True)
else:
    st.info("⏰ Market Closed or No breakout currently")
