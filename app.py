import streamlit as st
import pandas as pd
from utils.advanced_btst_scanner import fetch_btst_candidates

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(page_title="📈 Stock BTST/Intraday Screener", layout="wide")
st.title("📊 Intraday & BTST Stock Screener")
st.markdown("Get high-confidence bullish stock setups based on trend, volume, breakout, and momentum.")

# -------------------------------
# Load F&O stock list
# -------------------------------
try:
    with open("data/fno_stock_list.txt") as f:
        fno_stocks = [line.strip() for line in f.readlines() if line.strip()]
except FileNotFoundError:
    st.error("⚠️ 'data/fno_stock_list.txt' not found. Please upload the stock list file.")
    st.stop()

# -------------------------------
# User Inputs
# -------------------------------
col1, col2 = st.columns(2)
with col1:
    timeframe = st.selectbox("Select Timeframe", ["5","15m", "1h", "1d"], index=0)
with col2:
    min_conditions = st.slider("Minimum Conditions to Qualify", 2, 5, 3)

# -------------------------------
# Scanner Trigger
# -------------------------------
if st.button("🚀 Run Screener"):
    with st.spinner("Scanning stocks... this may take a few seconds"):
        results = fetch_btst_candidates(
            stock_list=fno_stocks,
            timeframe=timeframe,
            min_conditions=min_conditions,
            test_mode=False
        )

    if results:
        st.success(f"✅ Found {len(results)} potential setups!")
        df_results = pd.DataFrame(results)
        df_results = df_results[["Stock", "LTP", "Trend", "Confidence", "Reason", "TradingView"]]
        df_results["Chart"] = df_results["TradingView"].apply(lambda url: f"[📈 View]({url})")
        st.dataframe(df_results.drop(columns=["TradingView"]), use_container_width=True)
    else:
        st.warning("⚠️ No stock met the criteria.")

    # -----------------------------------
    # Logs and Skipped Stocks Display
    # -----------------------------------
    with st.expander("🛠️ View Skipped Stocks"):
        skipped = st.session_state.get("skipped_stocks", [])
        if skipped:
            df_skipped = pd.DataFrame(skipped).sort_values(by="RSI", ascending=False)
            st.dataframe(df_skipped, use_container_width=True)
        else:
            st.info("No skipped stocks logged.")

    with st.expander("📋 View Scan Logs"):
        logs = st.session_state.get("scan_logs", [])
        if logs:
            for log in logs:
                st.write(log)
        else:
            st.info("No scan issues logged.")
