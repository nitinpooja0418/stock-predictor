import numpy as np
import streamlit as st
import pandas as pd
from utils.nse_fno_scraper import get_fno_stocks
from utils.advanced_btst_scanner import fetch_btst_candidates
from component.trending_table import render_trending_table

# Page setup
st.set_page_config(page_title="Stock Trend Dashboard", layout="wide")
st.title("📈 AI Stock Trend & BTST Dashboard")

# -------------------------------
# Timeframe + Filter UI
# -------------------------------
timeframe = st.selectbox("⏱️ Select Timeframe", ["5m", "15m", "Daily"])
filter_option = st.selectbox("📊 Filter by Confidence / Trend", [
    "All", "Only 5/5", "4/5+", "BTST Setup"
])

with st.spinner("🔍 Scanning F&O stocks for BTST/trending setups..."):
    btst_data = fetch_btst_candidates(fno_stocks, timeframe=timeframe)

# -------------------------------
# Get F&O Stock List
# -------------------------------
with st.spinner("📡 Fetching live F&O stock list from NSE..."):
    fno_stocks = get_fno_stocks()

if not fno_stocks:
    st.error("❌ Failed to load F&O stock list. Please retry later or check fallback.")
    st.stop()

# -------------------------------
# Trending Stock Table
# -------------------------------
st.markdown("## 🔥 Trending Stocks (Breakout / Breakdown)")

try:
    trending_data = fetch_btst_candidates(fno_stocks)

    if filter_option == "Only 5/5":
        trending_data = [s for s in trending_data if s.get("Confidence", "").startswith("5")]
    elif filter_option == "4/5+":
        trending_data = [s for s in trending_data if s.get("Confidence", "").startswith(("4", "5"))]
    elif filter_option == "BTST Setup":
        trending_data = [s for s in trending_data if s.get("Trend") == "BTST Setup"]

    if trending_data:
        render_trending_table(trending_data)
    else:
        st.warning("No trending stocks found right now.")

except Exception as e:
    st.error(f"⚠️ Error while scanning trending stocks: {e}")

# -------------------------------
# BTST Candidates Section
# -------------------------------
st.markdown("---")
st.subheader("📊 BTST Stock Candidates (High Accuracy)")

with st.spinner("Scanning F&O stocks for BTST setups..."):
    btst_data = fetch_btst_candidates(fno_stocks)

if btst_data:
    st.success(f"✅ {len(btst_data)} strong BTST candidates found.")
    btst_df = pd.DataFrame(btst_data)
    st.dataframe(btst_df)
else:
    st.info("⚠️ No high-probability BTST candidates found at the moment.")
