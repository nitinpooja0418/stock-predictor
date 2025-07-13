import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
import streamlit as st

def fetch_btst_candidates(stock_list, timeframe="15m", min_conditions=2, test_mode=False):
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
                scan_logs.append(f"❌ Error with {symbol}: {required_cols}")
                continue

            df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
            df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()
            macd_indicator = MACD(close=df["Close"], window_slow=26, window_fast=12, window_sign=9)
            df["MACD"] = macd_indicator.macd()
            df["MACD_signal"] = macd_indicator.macd_signal()

            last = df.iloc[-1]
            prev = df.iloc[-2]

            reasons = []

            if last["Close"] > last["EMA20"]:
                reasons.append("Above EMA20")

      #      if last["Volume"] > prev["Volume"] * 1.5:
      #          reasons.append("Volume Spike")

            if last["RSI"] > 55:
                reasons.append("RSI > 55")

            if last["MACD"] > last["MACD_signal"]:
                reasons.append("MACD Crossover")

            if last["Close"] > df["High"].rolling(10).max().iloc[-2]:
                reasons.append("High Breakout")

            if len(reasons) >= min_conditions:
                trend_type = "BTST Setup" if timeframe in ["15m", "1d"] else "Intraday Setup"
                btst_stocks.append({
                    "Stock": symbol,
                    "Close": round(last["Close"], 2),
                    "Trend": trend_type,
                    "Confidence": f"{len(reasons)}/5",
                    "Reason": ", ".join(reasons),
                    "LTP": round(last["Close"], 2),
                    "RSI": round(last["RSI"], 2),
                    "TradingView": f"https://in.tradingview.com/symbols/NSE-{symbol}/"
                })
            else:
                skipped_stocks.append({"Stock": symbol, "RSI": round(last.get("RSI", 0), 2)})

        except Exception as e:
            scan_logs.append(f"⚠️ {symbol}: {e}")
            continue

    if not test_mode:
        st.session_state["skipped_stocks"] = skipped_stocks
        st.session_state["scan_logs"] = scan_logs

    return btst_stocks


# Show logs after scanning
if "scan_logs" in st.session_state:
    with st.expander("🪵 View Scan Logs"):
        for log in st.session_state["scan_logs"]:
            st.write(log)

if "skipped_stocks" in st.session_state:
    skipped_df = pd.DataFrame(st.session_state["skipped_stocks"])
    if not skipped_df.empty:
        st.markdown("### ⚠️ Skipped Stocks (Didn’t Meet Criteria)")
        top_skipped = skipped_df.sort_values(by="RSI", ascending=False).head(10)
        st.dataframe(top_skipped, use_container_width=True)

