import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
import streamlit as st
import time

def fetch_btst_candidates(stock_list, timeframe="15m", min_conditions=3, test_mode=False):
    btst_stocks = []
    skipped_stocks = []
    scan_logs = []

    for symbol in stock_list:
        try:
            period = "10d" if timeframe in ["15m", "1h"] else "6mo"
            df = yf.download(symbol + ".NS", period=period, interval=timeframe, progress=False)

            time.sleep(0.3)  # prevent rate-limiting

            if df.empty or len(df) < 30:
                scan_logs.append(f"{symbol}: Insufficient data")
                continue

            df = df.copy()
            df.dropna(inplace=True)

            # Ensure 1D columns
            for col in ["Close", "Volume", "High"]:
                if isinstance(df[col].iloc[0], (list, tuple, pd.Series, pd.DataFrame)):
                    df[col] = df[col].squeeze()

            # Validate required columns
            if not all(col in df.columns for col in ["Close", "Volume", "High"]):
                scan_logs.append(f"❌ {symbol}: Missing required columns")
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

            if last["Close"] > last["EMA20"]:
                reasons.append("Above EMA20")
            if last["Volume"] > prev["Volume"] * 1.5:
                reasons.append("Volume Spike")
            if last["MACD"] > last["MACD_signal"]:
                reasons.append("MACD Bullish Crossover")
            if last["RSI"] > 55:
                reasons.append(f"RSI Strong ({round(last['RSI'], 1)})")

            try:
                prev_high = df["High"].rolling(10).max().iloc[-2]
                if pd.notna(prev_high) and last["Close"] > prev_high:
                    reasons.append("10-Bar High Breakout")
            except Exception as e:
                scan_logs.append(f"{symbol}: High breakout error - {e}")

            if len(reasons) >= min_conditions:
                btst_stocks.append({
                    "Stock": symbol,
                    "Close": round(last["Close"], 2),
                    "Trend": "BTST Setup" if timeframe in ["15m", "1d"] else "Intraday Setup",
                    "Confidence": f"{len(reasons)}/5",
                    "Reason": ", ".join(reasons),
                    "LTP": round(last["Close"], 2),
                    "TradingView": f"https://in.tradingview.com/symbols/NSE-{symbol}/"
                })
            else:
                skipped_stocks.append({"Stock": symbol, "RSI": round(last.get("RSI", 0), 1)})

        except Exception as e:
            scan_logs.append(f"⚠️ {symbol}: {e}")
            continue

    if not test_mode:
        st.session_state["skipped_stocks"] = skipped_stocks
        st.session_state["scan_logs"] = scan_logs

    return btst_stocks
