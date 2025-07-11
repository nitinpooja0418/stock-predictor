import yfinance as yf
import pandas as pd
import numpy as np

def fetch_btst_candidates(stock_list):
    btst_candidates = []

    for symbol in stock_list:
        try:
            data = yf.download(f"{symbol}.NS", period="5d", interval="15m", progress=False)
            if len(data) < 20:
                continue

            data["EMA20"] = data["Close"].ewm(span=20).mean()
            data["AvgVol"] = data["Volume"].rolling(5).mean()
            data["VolumeSpike"] = data["Volume"] > (2 * data["AvgVol"])

            # Inside bar check (compare last 2 candles)
            data["InsideBar"] = (
                (data["High"] < data["High"].shift(1)) &
                (data["Low"] > data["Low"].shift(1))
            )

            latest = data.iloc[-1]
            prev = data.iloc[-2]

            conditions = [
                latest["Close"] > latest["EMA20"],
                latest["VolumeSpike"],
                prev["InsideBar"]
            ]

            if all(conditions):
                btst_candidates.append({
                    "Stock": symbol,
                    "LTP": round(latest["Close"], 2),
                    "Trend": "BTST Setup",
                    "Reason": "Breakout above 20 EMA + Inside Bar + Volume Spike"
                })

        except Exception as e:
            print(f"Error with {symbol}: {e}")
            continue

    return btst_candidates
