import streamlit as st
from utils.advanced_btst_scanner import fetch_btst_candidates
from component.trending_table import render_trending_table

st.set_page_config(page_title="Stock Trend Dashboard", layout="wide")

st.markdown("## 📈 Trending Stock Analysis (BTST + Breakout)")
timeframe = st.selectbox("Select Timeframe", ["5m", "15m", "Daily"])

# Sample F&O stocks list (you can expand this or fetch dynamically)
fno_stocks = [
    "RELIANCE", "ICICIBANK", "INFY", "HDFCBANK", "SBIN", "TCS",
    "ITC", "AXISBANK", "LT", "KOTAKBANK", "HINDUNILVR", "BAJFINANCE",
    "MARUTI", "ASIANPAINT", "HCLTECH", "ULTRACEMCO"
]

# Fetch BTST / breakout setup candidates
trending_data = []

try:
    trending_data = fetch_btst_candidates(fno_stocks)
except Exception as e:
    st.error(f"Error while fetching trend data: {e}")

if trending_data:
    render_trending_table(trending_data)
else:
    st.warning("⚠️ No trending stocks found based on current filters.")
