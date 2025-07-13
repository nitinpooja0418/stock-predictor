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
            close_series = df["Close"].squeeze() if hasattr(df["Close"], "squeeze") else df["Close"]
            df["EMA20"] = EMAIndicator(close=close_series, window=20).ema_indicator()
            df["RSI"] = RSIIndicator(close=close_series, window=14).rsi()
            
            macd = MACD(close=close_series)
            df["MACD"] = macd.macd()
            df["MACD_signal"] = macd.macd_signal()

            last = df.iloc[-1]
            prev = df.iloc[-2]

            reasons = []

            # Core bullish conditions
            if float(last["Close"]) > float(last["EMA20"]):
            reasons.append("Above EMA20")
        
            if float(last["Volume"]) > float(prev["Volume"]) * 1.5:
                reasons.append("Volume Spike")
            
            if float(last["MACD"]) > float(last["MACD_signal"]):
                reasons.append("MACD Bullish Crossover")
            
            if float(last["RSI"]) > 55:
                reasons.append(f"RSI Strong ({round(last['RSI'], 1)})")
            
            rolling_high = df["High"].rolling(10).max()
            if not rolling_high.isna().iloc[-2] and float(last["Close"]) > float(rolling_high.iloc[-2]):
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
