# trendfinder_app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time
import logging

# ------------------ Logging ------------------
logging.basicConfig(level=logging.INFO)

# ------------------ Functions ------------------
def get_stock_history(symbol, period='10d', interval='5m'):
    try:
        data = yf.download(symbol, period=period, interval=interval, progress=False)
        return data
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1*delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ------------------ Streamlit UI ------------------
st.title("Trend Finder - Breakout Scanner")
st.markdown("📈 Tracks high-beta breakout stocks every 5 minutes.")

stock_list = st.text_area(
    "Enter stock symbols separated by comma (e.g., TCS.NS, INFY.NS)",
    value="TCS.NS,INFY.NS"
).replace(" ", "").split(",")

placeholder = st.empty()

# ------------------ Main Loop ------------------
while True:
    breakout_stocks = []
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for stock_symbol in stock_list:
        hist = get_stock_history(stock_symbol)
        
        # Safe check for required columns
        required_cols = ['High','Low','Close','Volume']
        if hist.empty or not all(col in hist.columns for col in required_cols):
            logging.info(f"Skipping {stock_symbol}, missing columns or empty data")
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
        curr_rsi = hist['RSI'].iloc[-1] if not hist['RSI'].isnull().all() else 50
        
        # Breakout & RSI conditions
        if curr_close > max(last_10_high[:-1]) and curr_vol > avg_vol_10:
            if curr_rsi >= 60:
                breakout_stocks.append((stock_symbol, curr_close, curr_rsi))
    
    # Display in Streamlit
    with placeholder.container():
        st.subheader(f"Last Update: {current_time}")
        if breakout_stocks:
            df_display = pd.DataFrame(breakout_stocks, columns=['Symbol','Price','RSI'])
            st.dataframe(df_display)
        else:
            st.info("No breakout stocks at this interval.")
    
    time.sleep(300)  # 5 minutes
