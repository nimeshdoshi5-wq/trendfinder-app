import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

st.title("Trend Finder - Breakout Scanner")

# Stock list (aap future me NSE/F&O symbols add kar sakte ho)
stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]

# Function: fetch historical 10 min data
def fetch_data(symbol):
    try:
        df = yf.download(symbol, period="15d", interval="5m")
        if df.empty:
            return None
        return df
    except Exception as e:
        st.error(f"Error fetching {symbol}: {e}")
        return None

# Scan stocks
results = []
for stock in stocks:
    hist = fetch_data(stock)
    if hist is None or hist.empty:
        continue

    # Check columns
    if not all(x in hist.columns for x in ['High', 'Low', 'Volume', 'Close']):
        st.warning(f"{stock} data missing required columns")
        continue

    last_10_high = hist['High'].iloc[-10:].tolist()
    last_10_low = hist['Low'].iloc[-10:].tolist()
    last_10_vol = hist['Volume'].iloc[-10:].tolist()
    current_price = hist['Close'].iloc[-1]
    avg_vol = sum(last_10_vol) / len(last_10_vol)

    # Simple breakout condition
    if current_price > max(last_10_high[:-1]) and last_10_vol[-1] > avg_vol:
        results.append({
            "Stock": stock,
            "Current Price": current_price,
            "Breakout Level": max(last_10_high[:-1]),
            "Volume": last_10_vol[-1]
        })

# Display results
if results:
    st.subheader("Breakout Stocks (5 min scan)")
    st.table(pd.DataFrame(results))
else:
    st.info("No breakout detected in this scan.")

# Auto-refresh every 5 min
st.write(f"Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.experimental_rerun()
