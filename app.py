import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, time
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 5 minutes
st_autorefresh(interval=300000, key="refresh")

st.set_page_config(page_title="TrendFinder", layout="wide")
st.title("📈 TrendFinder - Breakout Beacon")

# Sidebar inputs
st.sidebar.header("Settings")
symbols_input = st.sidebar.text_area(
    "Enter Stock Symbols (comma separated, NSE example: RELIANCE.NS, TCS.NS):",
    "RELIANCE.NS, TCS.NS, INFY.NS"
)
symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]

lookback_days = st.sidebar.number_input("Lookback Days for Resistance/Volume", 5, 30, 10)
ema_period = st.sidebar.number_input("EMA Period", 5, 50, 20)

# Market time check
def is_market_open():
    now = datetime.now().time()
    return time(9, 15) <= now <= time(15, 30)

# Collect results
results = []

for symbol in symbols:
    try:
        df = yf.download(symbol, interval="5m", period="15d")
        if df.empty:
            continue
        
        # EMA calculation
        df["EMA"] = df["Close"].ewm(span=ema_period).mean()
        
        # Avg volume over last lookback_days
        avg_vol = df["Volume"].tail(lookback_days*78).mean()  # ~78 5-min candles per day
        
        latest = df.iloc[-1]
        prev_resistance = df["High"].rolling(lookback_days*78).max().iloc[-2]

        # Breakout condition
        condition = (
            latest["Close"] > latest["EMA"] and
            latest["Volume"] > avg_vol and
            latest["Close"] > prev_resistance
        )
        
        if condition:
            results.append({
                "Symbol": symbol,
                "Close": round(latest["Close"],2),
                "Volume": int(latest["Volume"]),
                "AvgVol": int(avg_vol),
                "EMA": round(latest["EMA"],2),
                "PrevResistance": round(prev_resistance,2)
            })
    except Exception as e:
        st.sidebar.error(f"{symbol}: {e}")

# Display results
if results:
    st.success("✅ Breakout Candidates Found")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)

    # Show chart for first breakout stock
    first_symbol = results[0]["Symbol"]
    df_chart = yf.download(first_symbol, interval="5m", period="5d")
    df_chart["EMA"] = df_chart["Close"].ewm(span=ema_period).mean()
    fig = px.line(df_chart, x=df_chart.index, y=["Close", "EMA"], title=f"{first_symbol} Chart")
    st.plotly_chart(fig, use_container_width=True)
else:
    if is_market_open():
        st.warning("⚠️ No breakout stocks right now.")
    else:
        st.info("⏰ Market Closed. App will show data during 9:15–15:30.")
