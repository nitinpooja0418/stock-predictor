import yfinance as yf
import pandas as pd
import pandas_ta as ta

def fetch_btst_candidates(fno_stocks):
    btst_candidates = []

    for symbol in fno_stocks:
        print(f"Processing: {symbol}")
        print(ta.ema(df["Close"], length=20).shape)

        try:
            df = yf.download(f"{symbol}.NS", period="5d", interval="15m", progress=False)
            if df.empty or "Close" not in df.columns:
                print(f"Skipping {symbol} — No data.")
                continue

            df.dropna(inplace=True)

            df["EMA20"] = ta.ema(df["Close"], length=20).squeeze()
            df["EMA50"] = ta.ema(df["Close"], length=50).squeeze()
            df["RSI"] = ta.rsi(df["Close"], length=14).squeeze()
            df["Volume_SMA20"] = df["Volume"].rolling(window=20).mean()

            last = df.iloc[-1]
            prev = df.iloc[-2]

            reasons = []

            if last["Close"] > last["EMA20"]:
                reasons.append("Above 20 EMA")
            if last["Volume"] > 1.2 * last["Volume_SMA20"]:
                reasons.append("Volume Spike")
            if last["RSI"] > 55:
                reasons.append("RSI > 55")
            if last["Close"] > prev["High"]:
                reasons.append("Breakout Candle")

            # Final filter: at least 3 confirmations
            if len(reasons) >= 3:
                btst_candidates.append({
                    "symbol": symbol,
                    "reasons": ", ".join(reasons)
                })

        except Exception as e:
            print(f"⚠️ Error processing {symbol}: {e}")
            continue

    return btst_candidates
