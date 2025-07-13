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

            # 🔍 Log row count for debugging
            scan_logs.append(f"{symbol}: Retrieved {len(df)} rows for {timeframe}")

            if df.empty or len(df) < 30:
                scan_logs.append(f"{symbol}: Insufficient data")
                continue

            df.dropna(inplace=True)

            required_cols = ["Close", "Volume", "High"]
            malformed = False
            for col in required_cols:
                if col not in df.columns:
                    scan_logs.append(f"{symbol}: Missing {col}")
                    malformed = True
                    break

                col_data = df[col]
                if isinstance(col_data, pd.DataFrame):
                    col_data = col_data.iloc[:, 0]
                df[col] = pd.Series(col_data.values.flatten(), index=df.index)

                if df[col].ndim != 1:
                    scan_logs.append(f"{symbol}: {col} still not 1D after flatten")
                    malformed = True
                    break

            if malformed:
                continue

            # Indicators (flattened)
            close_series = pd.Series(df["Close"].values.ravel(), index=df.index)
            df["EMA20"] = pd.Series(EMAIndicator(close=close_series, window=20).ema_indicator().values.ravel(), index=df.index)
            df["RSI"] = pd.Series(RSIIndicator(close=close_series, window=14).rsi().values.ravel(), index=df.index)

            macd = MACD(close=close_series)
            df["MACD"] = pd.Series(macd.macd().values.ravel(), index=df.index)
            df["MACD_signal"] = pd.Series(macd.macd_signal().values.ravel(), index=df.index)

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

            rolling_high = df["High"].rolling(10).max()
            if len(rolling_high) >= 2 and pd.notna(rolling_high.iloc[-2]):
                if last["Close"] > rolling_high.iloc[-2]:
                    reasons.append("10-Bar High Breakout")

            trend_type = "BTST Setup" if timeframe == "1d" else "Intraday Setup"
            if len(reasons) >= min_conditions:
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
                skipped_stocks.append({"Stock": symbol, "Reason": ", ".join(reasons)})

        except Exception as e:
            scan_logs.append(f"⚠️ {symbol}: {e}")
            continue

    if not test_mode:
        st.session_state["skipped_stocks"] = skipped_stocks
        st.session_state["scan_logs"] = scan_logs

    return btst_stocks

# Streamlit UI
st.set_page_config(page_title="Stock Scanner", layout="wide")
st.title("📈 BTST & Intraday Stock Scanner")

# Input file
with open("data/fno_stock_list.txt") as f:
    stock_list = [line.strip() for line in f if line.strip()]

# Select timeframe
timeframe = st.selectbox("Select Timeframe", ["5m", "15m", "1h", "1d"], index=0)

# Scan button
if st.button("🔍 Scan Stocks"):
    with st.spinner("Scanning, please wait..."):
        results = fetch_btst_candidates(stock_list, timeframe=timeframe, test_mode=False)

    if results:
        st.success(f"✅ {len(results)} stocks matched the criteria")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("⚠️ No stock met the criteria.")

    if "scan_logs" in st.session_state:
        with st.expander("View Logs"):
            for log in st.session_state["scan_logs"]:
                st.text(log)

    if "skipped_stocks" in st.session_state and st.session_state["skipped_stocks"]:
        with st.expander("Skipped Stocks"):
            skipped = st.session_state["skipped_stocks"]
            df_skipped = pd.DataFrame(skipped)
            st.dataframe(df_skipped)
