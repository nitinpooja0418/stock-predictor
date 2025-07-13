import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

def fetch_btst_candidates(stock_list, timeframe="15m"):
    btst_stocks = []

    # Map UI-friendly timeframe to yfinance format
    tf_map = {
        "5m": ("5d", "5m"),
        "15m": ("5d", "15m"),
        "Daily": ("3mo", "1d"),
        "1d": ("3mo", "1d")
    }

    period, interval = tf_map.get(timeframe, ("5d", "15m"))

    for symbol in stock_list:
        try:
            df = yf.download(
                symbol + ".NS",
                period=period,
                interval=interval,
                auto_adjust=False,
                progress=False
            )

            if df.empty or len(df) < 30:
                continue

            df.dropna(inplace=True)

            # Ensure Close is 1D
            if isinstance(df["Close"], pd.DataFrame):
                df["Close"] = df["Close"].squeeze()

            # Indicators
            df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
            df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()
            macd_obj = MACD(close=df["Close"])
            df["MACD"] = macd_obj.macd()
            df["MACD_Signal"] = macd_obj.macd_signal()

            df.dropna(inplace=True)
            if len(df) < 2:
                continue

            last = df.iloc[-1]
            prev = df.iloc[-2]
            reason = []

            if last["Close"] > last["EMA20"] and last["Volume"] > prev["Volume"] * 1.5:
                reason.append("Breakout Above EMA20 + Volume Spike")

            if last["RSI"] > 60:
                reason.append("Strong RSI")

            if last["Close"] > df["High"].rolling(10).max().iloc[-2]:
                reason.append("High Breakout")

            if last["MACD"] > last["MACD_Signal"]:
                reason.append("MACD Bullish Crossover")

            if len(reason) >= 2:
                btst_stocks.append({
                    "Stock": symbol,
                    "Close": round(last["Close"], 2),
                    "Trend": "BTST Setup",
                    "Confidence": f"{len(reason)}/4",
                    "Reason": ", ".join(reason),
                    "LTP": round(last["Close"], 2),
                    "TradingView": f"https://in.tradingview.com/symbols/NSE-{symbol}/"
                })

        except Exception as e:
            print(f"Error with {symbol}: {e}")
            continue

    return btst_stocks
