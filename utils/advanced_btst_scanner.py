import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

def fetch_btst_candidates(stock_list):
    btst_stocks = []

    for symbol in stock_list:
        try:
            df = yf.download(symbol + ".NS", period="5d", interval="15m", progress=False)

            if df.empty or len(df) < 20:
                continue

            df.dropna(inplace=True)
            df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
            df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()

            # Detect potential breakout
            last = df.iloc[-1]
            prev = df.iloc[-2]
            reason = []

            if last["Close"] > last["EMA20"] and last["Volume"] > prev["Volume"] * 1.5:
                reason.append("Breakout Above EMA20 + Volume Spike")

            if last["RSI"] > 60:
                reason.append("Strong RSI")

            if last["Close"] > df["High"].rolling(10).max().iloc[-2]:
                reason.append("High Breakout")

            if len(reason) >= 2:
                btst_stocks.append({
                    "Stock": symbol,
                    "Close": round(last["Close"], 2),
                    "Trend": "BTST Setup",
                    "Confidence": f"{len(reason)}/5",
                    "Reason": ", ".join(reason),
                    "LTP": round(last["Close"], 2),
                    "TradingView": f"https://in.tradingview.com/symbols/NSE-{symbol}/"
                })

        except Exception as e:
            print(f"Error with {symbol}: {e}")
            continue

    return btst_stocks
