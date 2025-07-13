import streamlit as st
import pandas as pd
from utils.advanced_btst_scanner import fetch_btst_candidates

# Load stock list
with open("data/fno_stock_list.txt") as f:
    fno_stocks = [line.strip() for line in f if line.strip()]

# Sidebar
scan_type = st.sidebar.selectbox("Select Scan Type", ["BTST", "Intraday"])
timeframe = "15m" if scan_type == "BTST" else "5m"

st.title("📈 Stock Trend Scanner")
st.markdown(f"Currently scanning for **{scan_type} setups** using `{timeframe}` timeframe...")

with st.spinner("🔍 Scanning stocks..."):
    results = fetch_btst_candidates(
        stock_list=fno_stocks,
        timeframe=timeframe,
        min_conditions=2,
        test_mode=False
    )

# Display results
if results:
    df = pd.DataFrame(results)
    df = df.sort_values(by="Confidence", ascending=False)
    st.success(f"✅ {len(df)} stock(s) found!")
    st.dataframe(df[["Stock", "LTP", "RSI", "Confidence", "Reason", "Trend", "TradingView"]], use_container_width=True)
else:
    st.warning("⚠️ No stock met the criteria.")

# Optional: Show skipped stocks
if "skipped_stocks" in st.session_state:
    st.markdown("### 📉 Skipped Stocks by RSI")
    df_skipped = pd.DataFrame(st.session_state["skipped_stocks"])
    if not df_skipped.empty and "RSI" in df_skipped.columns:
        st.dataframe(df_skipped.sort_values("RSI", ascending=False).head(10))
    else:
        st.info("No skipped stock data available.")

# Optional: Scan logs
if "scan_logs" in st.session_state:
    with st.expander("📝 View Scan Logs"):
        for log in st.session_state["scan_logs"]:
            st.text(log)
