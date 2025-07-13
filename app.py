import streamlit as st
import pandas as pd
from utils.advanced_btst_scanner import fetch_btst_candidates
from utils.nse_fno_scraper import get_fno_stocks

# Page setup
st.set_page_config(page_title="Stock Trend Dashboard", layout="wide")
st.title("📈 Intraday & BTST Stock Scanner")

# Timeframe selection
timeframe = st.selectbox("⏱️ Select Timeframe", ["5m", "15m", "1d"], index=1)

# -------------------------------
# Load F&O stock list
# -------------------------------
try:
    fno_stocks = get_fno_stocks()
except Exception as e:
    st.error(f"❌ Failed to fetch stock list: {e}")
    st.stop()

# -------------------------------
# Stock scanning
# -------------------------------
st.markdown("## 🔍 Scanning Stocks for BTST/Intraday Setups")

with st.spinner("Scanning all F&O stocks..."):
    results = fetch_btst_candidates(fno_stocks, timeframe=timeframe, min_conditions=3)

if results:
    df = pd.DataFrame(results)
    st.success(f"✅ {len(df)} potential stocks found")
    st.dataframe(df[['Stock', 'Close', 'Trend', 'Confidence', 'Reason']], use_container_width=True)
else:
    st.warning("⚠️ No stock met the criteria.")

# -------------------------------
# Logs for skipped stocks
# -------------------------------
st.markdown("---")
with st.expander("📄 View Skipped Stocks & Logs"):
    skipped = st.session_state.get("skipped_stocks", [])
    logs = st.session_state.get("scan_logs", [])

    if skipped:
        st.subheader("Skipped Stocks")
        st.dataframe(pd.DataFrame(skipped))
    if logs:
        st.subheader("Logs")
        for log in logs:
            st.text(log)
