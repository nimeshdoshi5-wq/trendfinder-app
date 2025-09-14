# app.py
import streamlit as st
import pandas as pd
import yfinance as yf
import time
import datetime
import logging

# ------------------ Setup Logging ------------------
logging.basicConfig(filename='error.log', level=logging.INFO)

# ------------------ Streamlit Page ------------------
st.set_page_config(page_title="Trend Finder - Breakout Scanner", layout="wide")
st.title("Trend Finder - Breakout Scanner")
st.text("Scanning high beta breakout stocks every 5 min...")

# ------------------ User Inputs ------------------
stock_list_input = st.text_area("Enter stock symbols separated by comma", "RELIANCE.NS,TCS.NS,INFY.NS")
stock_list = [s.strip() for s in stock_list_input.split(",")]

rsi_up = st.slider("RSI for Uptrend", 50, 100, 60)
rsi_down = st.slider("RSI for Downtrend", 0, 50, 40)

# ------------------ Helper Functions ------------------
def get_stock_history(symbol, period="10d", interval="5m"):
    try:
        data = yf.download(symbol, period=period, interval=interval)
        if data.empty:
            logging.info(f"No data for {symbol}")
        return data
    except Exception as e:
        logging.error(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()  # empty df to avoid crash

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / (avg_loss + 1e-6)
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ------------------ Main Scan Loop ------------------
placeholder = st.empty()

while True:
    breakout_stocks = []
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for stock_symbol in stock_list:
        hist = get_stock_history(stock_symbol)
        
        # Safe check
        if hist.empty or 'High' not in hist.columns or 'Low' not in hist.columns or 'Close' not in hist.columns or 'Volume' not in hist.columns:
            continue
        
        last_10_high = hist['High'].iloc[-10:].tolist()
        last_10_low = hist['Low'].iloc[-10:].tolist()
        last_10_close = hist['Close'].iloc[-10:].tolist()
        last_10_vol = hist['Volume'].iloc[-10:].tolist()
        
        # Current data
        curr_close = last_10_close[-1]
        curr_vol = last_10_vol[-1]
        avg_vol_10 = sum(last_10_vol[:-1])/len(last_10_vol[:-1]) if len(last_10_vol[:-1]) > 0 else 0
        
        # RSI
        hist['RSI'] = calculate_rsi(hist['Close'])
        curr_rsi = hist['RSI'].iloc[-1]
        
        # Conditions
        breakout = False
        if curr_close > max(last_10_high[:-1]) and curr_vol > avg_vol_10:
            if curr_rsi >= rsi_up:
                breakout = "UP"
            elif curr_rsi <= rsi_down:
                breakout = "DOWN"
        
        if breakout:
            breakout_stocks.append({
                "Stock": stock_symbol,
                "Close": curr_close,
                "Volume": curr_vol,
                "AvgVol10": avg_vol_10,
                "RSI": round(curr_rsi,2),
                "Direction": breakout
            })
    
    # Display results in Streamlit
    if breakout_stocks:
        df_display = pd.DataFrame(breakout_stocks)
        placeholder.table(df_display)
    else:
        placeholder.text(f"{current_time} - No breakout stocks found at this interval.")
    
    time.sleep(300)  # 5 min
