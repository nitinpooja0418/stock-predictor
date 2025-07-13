import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

def fetch_btst_candidates(stock_list, timeframe="15m", min_conditions=2):
    btst_stocks = []

    if timeframe == "5m":
        period = "2d"
    elif timeframe == "15m":
        period = "5d"
    else:  # daily
        timeframe = "1d"
        period = "30d"

    for symbol in stock_list:
        try:
            df = yf.download(symbol + ".NS", period=period, interval=timeframe, progress=False)

            if df.empty or len(df) < 20:
                continue

            df = df[["Close", "Volume", "High"]].dropna()
            if any(col not in df.columns or df[col].ndim != 1 for col in ["Close", "Volume", "High"]):
                print(f"❌ Skipping {symbol}: Missing column")
                continue

            df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
            df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()
            df["MACD_diff"] = MACD(close=df["Close"]).macd_diff()

            last = df.iloc[-1]
            prev = df.iloc[-2]
            reason = []

            if last["Close"] > last["EMA20"]:
                reason.append("Above EMA20")

            if last["RSI"] > 55:
                reason.append("RSI > 55")

            if last["MACD_diff"] > 0:
                reason.append("MACD Positive")

            if last["Volume"] > prev["Volume"] * 1.2:
                reason.append("Volume Spike")

            if last["Close"] > df["High"].rolling(10).max().iloc[-2]:
                reason.append("High Breakout")

            if len(reason) >= min_conditions:
                btst_stocks.append({
                    "Stock": symbol,
                    "Close": round(last["Close"], 2),
                    "Trend": "BTST Setup" if timeframe == "1d" else "Intraday Setup",
                    "Confidence": f"{len(reason)}/5",
                    "Reason": ", ".join(reason),
                    "LTP": round(last["Close"], 2),
                    "TradingView": f"https://in.tradingview.com/symbols/NSE-{symbol}/"
                })

        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")
            continue

    return btst_stocks
