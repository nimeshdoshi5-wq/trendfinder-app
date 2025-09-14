# trendfinder_safe.py
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)

st.title("Trend Finder - Breakout Scanner (Safe)")

# Stock symbols
stock_list = st.text_area(
    "Enter stock symbols separated by comma (e.g., TCS.NS, INFY.NS)",
    value="TCS.NS,INFY.NS"
).replace(" ", "").split(",")

placeholder = st.empty()

# RSI function
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1*delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=
