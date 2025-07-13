import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

def fetch_btst_candidates(stock_list, timeframe="15m"):
    btst_stocks = []

    # Set period based on timeframe
    if timeframe == "5m":
        period = "2d"
    elif timeframe == "15m":
        period = "5d"
    else:  # "1d" or "daily"
        timeframe = "1d"
        period = "30d"

    for symbol in stock_list:
        try:
            df = yf.download(symbol + ".NS", period=period, interval=timeframe, progress=False)

            # Skip if data is missing or too short
            if df.empty or len(df) < 20:
                continue

            df = df[["Close", "Volume", "High"]].dropna()

            # Ensure all required columns are present and 1D
            for col in ["Close", "Volume", "High"]:
                if col not in df.columns or df[col].ndim != 1:
                    raise ValueError(f"{symbol}: Missing or invalid column - {col}")

            # Indicators
            df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
            df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()
            macd = MACD(close=df["Close"])
            df["MACD_diff"] = macd.macd_diff()

            last = df.iloc[-1]
            prev = df.iloc[-2]
            reason = []

            # Rule 1: Above EMA with volume spike
            if last["Close"] > last["EMA20"] and last["Volume"] > prev["Volume"] * 1.5:
                reason.append("Breakout Above EMA + Volume Spike")

            # Rule 2: RSI strong
            if last["RSI"] > 60:
                reason.append("Strong RSI")

            # Rule 3: High breakout
            if last["Close"] > df["High"].rolling(10).max().iloc[-2]:
                reason.append("High Breakout")

            # Rule 4: MACD crossover
            if last["MACD_diff"] > 0 and prev["MACD_diff"] <= 0:
                reason.append("MACD Bullish Crossover")

            if len(reason) >= 2:
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
