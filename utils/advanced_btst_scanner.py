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
                scan_logs.append(f"⚠️ {symbol}: Insufficient data")
                continue

            df.dropna(inplace=True)

            required_cols = ["Close", "Volume", "High"]
            malformed = False
            for col in required_cols:
                if col not in df.columns:
                    scan_logs.append(f"⚠️ {symbol}: Missing {col} column")
                    malformed = True
                    break
                col_values = df[col].values
                if col_values.ndim > 1:
                    df[col] = pd.Series(col_values.flatten(), index=df.index)
                if df[col].ndim != 1:
                    scan_logs.append(f"⚠️ {symbol}: {col} is not 1D after flattening")
                    malformed = True
                    break
            if malformed:
                continue

            df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
            df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()
            macd = MACD(close=df["Close"])
            df["MACD"] = macd.macd()
            df["MACD_signal"] = macd.macd_signal()

            last = df.iloc[-1]
            prev = df.iloc[-2]

            reasons = []

            if float(last["Close"]) > float(last["EMA20"]):
                reasons.append("Above EMA20")

            if pd.notna(last["Volume"]) and pd.notna(prev["Volume"]):
                if float(last["Volume"]) > float(prev["Volume"]) * 1.5:
                    reasons.append("Volume Spike")

            if float(last["MACD"]) > float(last["MACD_signal"]):
                reasons.append("MACD Bullish Crossover")

            if float(last["RSI"]) > 55:
                reasons.append(f"RSI Strong ({round(last['RSI'], 1)})")

            rolling_high = df["High"].rolling(10).max()
            if len(rolling_high) >= 2 and float(last["Close"]) > float(rolling_high.iloc[-2]):
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
            scan_logs.append(f"⚠️ {symbol}: {str(e)}")
            continue

    if not test_mode:
        st.session_state["skipped_stocks"] = skipped_stocks
        st.session_state["scan_logs"] = scan_logs

    return btst_stocks

# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="Stock Scanner", layout="wide")
st.title("📈 BTST & Intraday Stock Scanner")

# Load FNO stock list from text file
with open("data/fno_stock_list.txt") as f:
    stock_list = [line.strip() for line in f if line.strip()]

# Timeframe selection (with 5m support)
timeframe = st.selectbox("Select Timeframe", ["5m", "15m", "1h", "1d"], index=0)

# Scan trigger
if st.button("🔍 Scan Stocks"):
    with st.spinner("Scanning stocks, please wait..."):
        results = fetch_btst_candidates(stock_list, timeframe=timeframe, test_mode=False)

    if results:
        st.success(f"✅ {len(results)} stocks matched the criteria")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("⚠️ No stock met the criteria.")

    if "scan_logs" in st.session_state:
        with st.expander("⚙️ Scan Logs"):
            for log in st.session_state["scan_logs"]:
                st.text(log)

    if "skipped_stocks" in st.session_state and st.session_state["skipped_stocks"]:
        with st.expander("🚫 Skipped Stocks"):
            st.dataframe(pd.DataFrame(st.session_state["skipped_stocks"]))
