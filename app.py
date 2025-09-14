import streamlit as st
import time
import yfinance as yf
from libs.scanner import calculate_rsi, price_gain, check_breakout_gain

st.title("Trend Finder - Breakout Scanner")

# Example stocks
symbols = ["TCS.NS", "RELIANCE.NS", "INFY.NS"]

SCAN_INTERVAL = 300  # 5 minutes
RSI_UPPER = 60
RSI_LOWER = 40

while True:
    for symbol in symbols:
        # Fetch last 11 days of historical data
        hist = yf.download(symbol, period="11d", interval="1d")
        last_10_high = hist['High'].iloc[:-1].tolist()
        last_10_low = hist['Low'].iloc[:-1].tolist()
        avg_volume = hist['Volume'].iloc[:-1].mean()
        current_price = hist['Close'].iloc[-1]
        previous_close = hist['Close'].iloc[-2]
        volume = hist['Volume'].iloc[-1]

        data = {
            'lastPrice': current_price,
            'previousClose': previous_close,
            'volume': volume
        }

        rsi = calculate_rsi(hist['Close'].tolist())
        trend = check_breakout_gain(data, last_10_high, last_10_low, avg_volume)

        if trend:
            if trend == "Uptrend" and rsi > RSI_UPPER:
                st.write(f"{symbol} 🔺 Uptrend | Gain: {price_gain(data):.2f}% | RSI: {rsi:.2f}")
            elif trend == "Downtrend" and rsi < RSI_LOWER:
                st.write(f"{symbol} 🔻 Downtrend | Loss: {price_gain(data):.2f}% | RSI: {rsi:.2f}")
    time.sleep(SCAN_INTERVAL)
