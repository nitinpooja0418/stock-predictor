import numpy as np
import streamlit as st
import pandas as pd
from utils.nse_fno_scraper import get_fno_stocks
from utils.advanced_btst_scanner import fetch_btst_candidates
from component.trending_table import render_trending_table

results = fetch_btst_candidates(["RELIANCE"], timeframe="15m")
print(results)

# Page setup
st.set_page_config(page_title="Stock Trend Dashboard", layout="wide")
st.title("📈 AI Stock Trend & BTST Dashboard")

# -------------------------------
# Timeframe + Filter UI
# -------------------------------
timeframe = st.selectbox("⏱️ Select Timeframe", ["5m", "15m", "Daily"])
filter_option = st.selectbox("📊 Filter by Confidence / Trend", [
    "All", "Only 4/4", "3/4+", "BTST Setup"
])

# -------------------------------
# Get F&O Stock List
# -------------------------------
with st.spinner("📡 Fetching live F&O stock list from NSE..."):
    fno_stocks = get_fno_stocks()

if not fno_stocks:
    st.error("❌ Failed to load F&O stock list. Please retry later or check fallback.")
    st.stop()

# -------------------------------
# BTST Candidates Section
# -------------------------------
st.markdown("---")
st.subheader("📊 BTST Stock Candidates (High Accuracy)")

with st.spinner("🔍 Scanning F&O stocks for BTST setups..."):
    btst_data = fetch_btst_candidates(fno_stocks, timeframe=timeframe)

# -------------------------------
# Trending Stock Table
# -------------------------------
st.markdown("## 🔥 Trending Stocks (Breakout / Breakdown)")

try:
    filtered_data = btst_data.copy()

    if filter_option == "Only 4/4":
        filtered_data = [s for s in filtered_data if s.get("Confidence") == "4/4"]
    elif filter_option == "3/4+":
        filtered_data = [s for s in filtered_data if s.get("Confidence", "").startswith(("3", "4"))]
    elif filter_option == "BTST Setup":
        filtered_data = [s for s in filtered_data if s.get("Trend") == "BTST Setup"]

    if filtered_data:
        render_trending_table(filtered_data)
    else:
        st.warning("No trending stocks found right now.")

except Exception as e:
    st.error(f"⚠️ Error while scanning trending stocks: {e}")

# -------------------------------
# Show Raw DataFrame
# -------------------------------
if btst_data:
    st.success(f"✅ {len(btst_data)} strong BTST candidates found.")
    st.dataframe(pd.DataFrame(btst_data))
else:
    st.info("⚠️ No high-probability BTST candidates found at the moment.")
