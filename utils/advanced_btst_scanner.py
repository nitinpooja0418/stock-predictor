import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
import streamlit as st

def fetch_btst_candidates(stock_list, timeframe="15m", min_conditions=3, test_mode=False):
    btst_stocks = []
    skipped_stocks = []
    scan_logs = []

    for symbol in stock_list:
        try:
            df = yf.download(symbol + ".NS", period="5d", interval=timeframe, progress=False)

            if df.empty or len(df) < 30:
                scan_logs.append(f"{symbol}: Insufficient data")
                continue

            df.dropna(inplace=True)

            required_cols = ["Close", "Volume", "High"]
            if not all(col in df.columns for col in required_cols):
                scan_logs.append(f"❌ Error with {symbol}: Missing {required_cols}")
                continue

            # Indicators
            df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
            df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()
            macd = MACD(close=df["Close"])
            df["MACD"] = macd.macd()
            df["MACD_signal"] = macd.macd_signal()

            last = df.iloc[-1]
            prev = df.iloc[-2]

            reasons = []

            # Core bullish conditions
            if last["Close"] > last["EMA20"]:
                reasons.append("Above EMA20")

            if last["Volume"] > prev["Volume"] * 1.5:
                reasons.append("Volume Spike")

            if last["MACD"] > last["MACD_signal"]:
                reasons.append("MACD Bullish Crossover")

            if last["RSI"] > 55:
                reasons.append(f"RSI Strong ({round(last['RSI'], 1)})")

            if last["Close"] > df["High"].rolling(10).max().iloc[-2]:
                reasons.append("10-Bar High Breakout")

            # Final decision
            if len(reasons) >= min_conditions:
                trend_type = "BTST Setup" if timeframe in ["15m", "1d"] else "Intraday Setup"
                btst_stocks.append({
                    "Stock": symbol,
                    "Close": round(last["Close"], 2),
                    "Trend": trend_type,
                    "Confidence": f"{len(reasons)}/5",
                    "Reason": ", ".join(reasons),
                    "LTP": round(last["Close"], 2),
                    "TradingView": f"https://in.tradingview.com/symbols/NSE-{symbol}/"
                })
            else:
                skipped_stocks.append({"Stock": symbol, "RSI": round(last["RSI"], 1)})

        except Exception as e:
            scan_logs.append(f"⚠️ {symbol}: {e}")
            continue

    if not test_mode:
        st.session_state["skipped_stocks"] = skipped_stocks
        st.session_state["scan_logs"] = scan_logs

    return btst_stocks
