import yfinance as yf
import pandas as pd
import numpy as np

def fetch_btst_candidates(stock_list):
    btst_candidates = []

    for symbol in stock_list:
        try:
            # Fetch 15-min data of last 5 days
            data = yf.download(f"{symbol}.NS", period="5d", interval="15m", progress=False)
            if len(data) < 30:
                continue

            # === Indicators ===
            data["EMA20"] = data["Close"].ewm(span=20).mean()
            data["EMA50"] = data["Close"].ewm(span=50).mean()
            data["AvgVol"] = data["Volume"].rolling(5).mean()
            data["RSI"] = compute_rsi(data["Close"])

            # === Price Action ===
            data["InsideBar"] = (data["High"] < data["High"].shift(1)) & (data["Low"] > data["Low"].shift(1))
            data["VolumeSpike"] = data["Volume"] > 1.5 * data["AvgVol"]
            data["Trend"] = data["EMA20"] > data["EMA50"]
            data["BreakoutHigh"] = data["Close"] > data["High"].shift(1).rolling(20).max()

            latest = data.iloc[-1]
            prev = data.iloc[-2]

            # === Conditions (Score Based) ===
            score = 0
            reasons = []

            if latest["Trend"]:
                score += 1
                reasons.append("20 EMA > 50 EMA")

            if latest["BreakoutHigh"]:
                score += 1
                reasons.append("Structure Breakout")

            if latest["VolumeSpike"]:
                score += 1
                reasons.append("Volume Spike")

            if prev["InsideBar"]:
                score += 1
                reasons.append("Inside Bar")

            if latest["RSI"] > 55:
                score += 1
                reasons.append(f"RSI {int(latest['RSI'])} > 55")

            # === Final filter ===
            if score >= 4:
                btst_candidates.append({
                    "Stock": symbol,
                    "LTP": round(latest["Close"], 2),
                    "% Change": round(((latest["Close"] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100, 2),
                    "Trend": "BTST Setup",
                    "Reason": " + ".join(reasons)
                })

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue

    return btst_candidates


# === Helper: RSI Calculation ===
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return pd.Series(rsi, index=series.index)
