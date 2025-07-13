import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
import sys

def fetch_btst_candidates(stock_list, timeframe="15m", test_mode=False):
    btst_stocks = []

    # Map timeframe for yfinance
    tf_map = {
        "5m": ("5d", "5m"),
        "15m": ("5d", "15m"),
        "Daily": ("3mo", "1d")
    }

    period, interval = tf_map.get(timeframe, ("5d", "15m"))

    for symbol in stock_list:
        try:
            df = yf.download(
                f"{symbol}.NS",
                period=period,
                interval=interval,
                auto_adjust=False,
                progress=False
            )

            if df.empty or len(df) < 30:
                if test_mode:
                    print(f"{symbol}: Not enough data.")
                continue

            df.dropna(subset=["Close", "Volume", "High"], inplace=True)

            close = df["Close"].astype(float)
            volume = df["Volume"].astype(float)
            high = df["High"].astype(float)

            # Technical indicators
            df["EMA20"] = EMAIndicator(close=close, window=20).ema_indicator()
            df["RSI"] = RSIIndicator(close=close, window=14).rsi()
            macd = MACD(close=close)
            df["MACD"] = macd.macd()
            df["MACD_Signal"] = macd.macd_signal()

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
                result = {
                    "Stock": symbol,
                    "Close": round(last["Close"], 2),
                    "Trend": "BTST Setup",
                    "Confidence": f"{len(reason)}/4",
                    "Reason": ", ".join(reason),
                    "LTP": round(last["Close"], 2),
                    "TradingView": f"https://in.tradingview.com/symbols/NSE-{symbol}/"
                }

                if test_mode:
                    print(f"\n✅ Test Result for {symbol}:\n{result}\n")
                else:
                    btst_stocks.append(result)

        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")
            continue

    return btst_stocks


# --------------------------------------
# 🔍 TEST MODE: Run via CLI for 1 stock
# --------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        stock = sys.argv[1]
        print(f"Testing single stock: {stock}")
        fetch_btst_candidates([stock], timeframe="15m", test_mode=True)
    else:
        print("Usage: python advanced_btst_scanner.py <NSE_STOCK_SYMBOL>")
