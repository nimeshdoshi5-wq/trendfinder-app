import numpy as np
import pandas as pd

def calculate_rsi(prices, period=14):
    delta = np.diff(prices)
    up, down = delta.clip(min=0), -delta.clip(max=0)
    roll_up = pd.Series(up).rolling(period).mean()
    roll_down = pd.Series(down).rolling(period).mean()
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def price_gain(data):
    return ((data['lastPrice'] - data['previousClose']) / data['previousClose']) * 100

def check_breakout_gain(data, last_10_days_high, last_10_days_low, avg_volume_last_10_days):
    current_price = data['lastPrice']
    volume = data['volume']
    gain = price_gain(data)

    if current_price > max(last_10_days_high) and volume > avg_volume_last_10_days and gain > 0:
        return "Uptrend"
    elif current_price < min(last_10_days_low) and volume > avg_volume_last_10_days and gain < 0:
        return "Downtrend"
    return None
