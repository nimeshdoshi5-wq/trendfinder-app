import streamlit as st
import pandas as pd
import plotly.express as px
from nsepython import nse_fno_lot_sizes, nse_fetch, nse_quote, nse_sector
from datetime import datetime, time
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Auto-refresh every 5 minutes
st_autorefresh(interval=300000, key="refresh")

# -----------------------------
# Page setup
st.set_page_config(page_title="TrendFinder Pro+ NSE", layout="wide")
st.title("📈 TrendFinder Pro+ - NSE Breakout Scanner (F&O + Indices)")

# -----------------------------
# Sidebar settings
st.sidebar.header("Settings")
lookback_days = st.sidebar.number_input("Lookback Days for Resistance/Support", 5, 30, 10)
ema_period = st.sidebar.number_input("EMA Period", 5, 50, 20)

# -----------------------------
# Market time check
def is_market_open():
    now = datetime.now().time()
    return time(9, 15) <= now <= time(15, 30)

# -----------------------------
# Indicators
def calculate_ema(df, period=20):
    return df['Close'].ewm(span=period).mean()

def calculate_vwap(df):
    return (df['Close']*df['Volume']).cumsum()/df['Volume'].cumsum()

def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -1*delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100/(1+rs))
    return rsi

# -----------------------------
# Fetch NSE data function
def fetch_nse_data(symbol, interval="5m", days=10):
    try:
        df = nse_fetch(symbol, interval, days)
        if df.empty:
            df = nse_fetch(symbol, "1d", 10)  # fallback daily
        df["Close"] = df["close"].astype(float)
        df["High"] = df["high"].astype(float)
        df["Low"] = df["low"].astype(float)
        df["Volume"] = df["volume"].astype(float)
        return df
    except:
        return pd.DataFrame()

# -----------------------------
# F&O + Indices symbols
fno_symbols = list(nse_fno_lot_sizes().keys())  # all F&O symbols (~200)
indices = ["NIFTY", "BANKNIFTY", "SENSEX"]
symbols = fno_symbols + indices

# -----------------------------
# Sector info
sector_map = {}
for s in symbols:
    try:
        info = nse_sector(s)
        sector_map[s] = info.get("industry", "Unknown")
    except:
        sector_map[s] = "Unknown"

# -----------------------------
# Collect results
results = []

for symbol in symbols:
    df = fetch_nse_data(symbol)
    if df.empty:
        continue

    df["EMA"] = calculate_ema(df, ema_period)
    df["VWAP"] = calculate_vwap(df)
    df["RSI"] = calculate_rsi(df, 14)

    latest = df.iloc[-1]
    avg_vol = df['Volume'].tail(lookback_days*78 if len(df)>78 else len(df)).mean()
    prev_res = df['High'].rolling(lookback_days*78 if len(df)>78 else len(df)).max().iloc[-2]
    prev_sup = df['Low'].rolling(lookback_days*78 if len(df)>78 else len(df)).min().iloc[-2]

    beta = 1.2  # placeholder

    upside = latest['Close']>prev_res and latest['Close']>latest['VWAP'] and latest['RSI']>60 and latest['Volume']>avg_vol
    downside = latest['Close']<prev_sup and latest['Close']<latest['VWAP'] and latest['RSI']<40 and latest['Volume']>avg_vol

    results.append({
        "Symbol": symbol,
        "Sector": sector_map.get(symbol, "Unknown"),
        "Close": round(latest['Close'],2),
        "Breakout": "▲" if upside else ("▼" if downside else "-"),
        "EMA": round(latest['EMA'],2),
        "VWAP": round(latest['VWAP'],2),
        "RSI": round(latest['RSI'],2),
        "Beta": beta
    })

# -----------------------------
# Display results

if results:
    df_results = pd.DataFrame(results)

    # Color breakout arrows
    def color_arrow(val):
        if val=="▲":
            return 'color: green; font-weight: bold;'
        elif val=="▼":
            return 'color: red; font-weight: bold;'
        else:
            return ''

    st.subheader("All F&O + Indices Breakout / Breakdown")
    st.dataframe(df_results.style.applymap(color_arrow, subset=['Breakout']), use_container_width=True)

    # Sector-wise expandable
    sectors = df_results['Sector'].unique()
    for sec in sectors:
        sec_df = df_results[df_results['Sector']==sec]
        if not sec_df.empty:
            with st.expander(f"{sec} sector"):
                st.dataframe(sec_df.style.applymap(color_arrow, subset=['Breakout']), use_container_width=True)

    # Chart for first breakout stock
    breakout_stocks = [r for r in results if r['Breakout']=="▲"]
    if breakout_stocks:
        first_symbol = breakout_stocks[0]['Symbol']
        df_chart = fetch_nse_data(first_symbol, interval="5m", days=5)
        df_chart["EMA"] = calculate_ema(df_chart, ema_period)
        fig = px.line(df_chart, x=df_chart.index, y=["Close", "EMA"], title=f"{first_symbol} Chart")
        st.plotly_chart(fig, use_container_width=True)

else:
    if is_market_open():
        st.warning("⚠️ No breakout stocks right now.")
    else:
        st.info("⏰ Market Closed or showing last available data.")
