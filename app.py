import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 5 minutes
st_autorefresh(interval=300000, key="refresh")

st.set_page_config(page_title="TrendFinder Pro+ F&O & Indices", layout="wide")
st.title("📈 TrendFinder Pro+ - Breakout Scanner (F&O + Indices)")

# Sidebar
st.sidebar.header("Settings")
symbols_input = st.sidebar.text_area(
    "Enter Stock Symbols (comma separated, NSE example: RELIANCE.NS, TCS.NS, INFY.NS, NIFTY50.NS, BANKNIFTY.NS, SENSEX.BO):",
    "RELIANCE.NS, TCS.NS, INFY.NS, HDFC.NS, ICICIBANK.NS, NIFTY50.NS, BANKNIFTY.NS, SENSEX.BO"
)
symbols_input = [s.strip() for s in symbols_input.split(",") if s.strip()]

# Example full F&O list (200+ symbols)
fo_symbols = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFC.NS","ICICIBANK.NS",
    # ... add all 200+ F&O symbols here
]

indices = ["NIFTY50.NS", "BANKNIFTY.NS", "SENSEX.BO"]
symbols = [s for s in symbols_input if s in fo_symbols + indices]

lookback_days = st.sidebar.number_input("Lookback Days for Resistance/Volume", 5, 30, 10)
ema_period = st.sidebar.number_input("EMA Period", 5, 50, 20)

# Market open check
def is_market_open():
    now = datetime.now().time()
    return time(9, 15) <= now <= time(15, 30)

# RSI calculation
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1*delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100/(1+rs))
    return rsi

# Latest candle
def get_latest(df):
    if df.empty:
        return None
    return df.iloc[-1]

# Sector assignment
def get_sector(symbol):
    if symbol in indices:
        return "Indices"
    return yf.Ticker(symbol).info.get("sector", "Unknown")

results = []

# Fetch data
for symbol in symbols:
    try:
        interval = "5m" if symbol not in indices else "1d"
        df = yf.download(symbol, interval=interval, period="15d" if interval=="5m" else "30d")
        latest = get_latest(df)
        if latest is None:
            continue

        # EMA, VWAP, RSI
        df["EMA"] = df["Close"].ewm(span=ema_period).mean()
        df["VWAP"] = (df['Close']*df['Volume']).cumsum()/df['Volume'].cumsum()
        df["RSI"] = calculate_rsi(df["Close"],14)

        avg_vol = df["Volume"].tail(lookback_days*78 if interval=="5m" else lookback_days).mean()
        prev_res = float(df["High"].rolling(lookback_days*78 if interval=="5m" else lookback_days).max().iloc[-2])
        prev_sup = float(df["Low"].rolling(lookback_days*78 if interval=="5m" else lookback_days).min().iloc[-2])

        latest_close = float(latest["Close"])
        latest_vwap = float(latest["VWAP"])
        latest_rsi = float(latest["RSI"])
        latest_vol = float(latest["Volume"])
        beta = yf.Ticker(symbol).info.get("beta",1)
        sector = get_sector(symbol)

        # Breakout logic
        upside = (latest_close>prev_res and latest_close>latest_vwap and latest_rsi>60 and beta>1 and latest_vol>avg_vol)
        downside = (latest_close<prev_sup and latest_close<latest_vwap and latest_rsi<40 and beta>1 and latest_vol>avg_vol)

        results.append({
            "Symbol": symbol,
            "Close": round(latest_close,2),
            "Volume": int(latest_vol),
            "AvgVol": int(avg_vol),
            "EMA": round(float(latest["EMA"]),2),
            "VWAP": round(latest_vwap,2),
            "RSI": round(latest_rsi,2),
            "Beta": round(beta,2),
            "Breakout": "▲" if upside else ("▼" if downside else "-"),
            "Sector": sector
        })

    except Exception as e:
        st.sidebar.error(f"{symbol}: {e}")

# Sector-wise display
if results:
    sector_dict = {}
    for r in results:
        sec = r["Sector"]
        if sec not in sector_dict:
            sector_dict[sec] = []
        sector_dict[sec].append(r)

    for sector_name, items in sector_dict.items():
        with st.expander(sector_name):
            indices_list = [x for x in items if x["Symbol"] in indices]
            stocks_list = [x for x in items if x["Symbol"] not in indices]
            combined = indices_list + stocks_list
            df_sector = pd.DataFrame(combined)
            st.dataframe(df_sector.style.applymap(
                lambda x: 'color: green;' if x=="▲" else ('color: red;' if x=="▼" else ''), subset=["Breakout"]
            ), use_container_width=True)

    # Chart for first breakout
    breakout_stocks = [r["Symbol"] for r in results if r["Breakout"] in ["▲","▼"]]
    if breakout_stocks:
        first_symbol = breakout_stocks[0]
        interval_chart = "5m" if first_symbol not in indices else "1d"
        df_chart = yf.download(first_symbol, interval=interval_chart, period="5d")
        df_chart["EMA"] = df_chart["Close"].ewm(span=ema_period).mean()
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df_chart.index, open=df_chart['Open'], high=df_chart['High'],
            low=df_chart['Low'], close=df_chart['Close'], name="Candlestick"
        ))
        fig.add_trace(go.Scatter(
            x=df_chart.index, y=df_chart['EMA'], mode='lines', name=f"EMA {ema_period}", line=dict(color='blue')
        ))
        fig.update_layout(title=f"{first_symbol} Chart", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("⏰ Market Closed or No breakout stocks currently. Showing last available data.")
