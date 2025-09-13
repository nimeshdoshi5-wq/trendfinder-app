import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 5 minutes
st_autorefresh(interval=300000, key="refresh")

st.set_page_config(page_title="TrendFinder Pro+", layout="wide")
st.title("📈 TrendFinder Pro+ - Breakout Scanner")

# Sidebar settings
st.sidebar.header("Settings")
symbols_input = st.sidebar.text_area(
    "Enter Stock Symbols (comma separated, NSE example: RELIANCE.NS, TCS.NS):",
    "RELIANCE.NS, TCS.NS, INFY.NS"
)
symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]

lookback_days = st.sidebar.number_input("Lookback Days for Resistance/Volume", 5, 30, 10)
ema_period = st.sidebar.number_input("EMA Period", 5, 50, 20)

# Market open check
def is_market_open():
    now = datetime.now().time()
    return time(9, 15) <= now <= time(15, 30)

# RSI Calculation
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1*delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100/(1+rs))
    return rsi

# Collect results
results = []

for symbol in symbols:
    try:
        df = yf.download(symbol, interval="5m", period="15d")
        if df.empty:
            continue
        
        # EMA
        df["EMA"] = df["Close"].ewm(span=ema_period).mean()
        # VWAP
        df["VWAP"] = (df['Close']*df['Volume']).cumsum() / df['Volume'].cumsum()
        # RSI
        df["RSI"] = calculate_rsi(df["Close"], 14)
        
        avg_vol = df["Volume"].tail(lookback_days*78).mean()
        latest = df.iloc[-1]
        prev_resistance = df["High"].rolling(lookback_days*78).max().iloc[-2]
        prev_support = df["Low"].rolling(lookback_days*78).min().iloc[-2]
        
        # Beta
        beta = yf.Ticker(symbol).info.get("beta", 1)

        # Upside breakout
        upside = latest["Close"] > prev_resistance and latest["Close"] > latest["VWAP"] and latest["RSI"]>60 and beta>1 and latest["Volume"]>avg_vol
        # Downside breakout
        downside = latest["Close"] < prev_support and latest["Close"] < latest["VWAP"] and latest["RSI"]<40 and bet_
