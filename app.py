import streamlit as st
import pandas as pd
from utils.nse_fno_scraper import get_fno_stocks
from utils.advanced_btst_scanner import fetch_btst_candidates
from component.trending_table import render_trending_table

# Page setup
st.set_page_config(page_title="Stock Trend Dashboard", layout="wide")
st.title("📈 AI Stock Trend & BTST Dashboard")

# Timeframe selector
timeframe = st.selectbox("⏱️ Select Timeframe", ["5m", "15m", "Daily"])
filter_option = st.selectbox("📊 Filter by Confidence / Trend", [
    "All", "Only 5/5", "4/5+", "BTST Setup"
])

# --- Single Stock Testing ---
st.markdown("### 🔍 Test a Single Stock (Optional)")
single_stock = st.text_input("Enter NSE Stock Symbol (e.g., RELIANCE, TCS, INFY)", "")

if single_stock:
    st.info(f"Running analysis for `{single_stock.upper()}`...")
    single_result = fetch_btst_candidates([single_stock.upper()], timeframe=timeframe, test_mode=True)

    if single_result:
        st.success("✅ BTST setup detected!")
        df = pd.DataFrame(single_result)
        st.dataframe(df)
    else:
        st.warning("⚠️ No valid BTST setup found for this stock.")
    st.stop()  # Stop further processing if testing single stock

# --- Full F&O List Analysis ---
with st.spinner("📡 Fetching F&O stock list..."):
    fno_stocks = get_fno_stocks()

if not fno_stocks:
    st.error("❌ Could not load F&O list.")
    st.stop()

st.markdown("## 🔥 Trending Stocks (Breakout / BTST)")

try:
    btst_data = fetch_btst_candidates(fno_stocks, timeframe=timeframe)

    if filter_option == "Only 5/5":
        btst_data = [s for s in btst_data if s.get("Confidence", "").startswith("5")]
    elif filter_option == "4/5+":
        btst_data = [s for s in btst_data if s.get("Confidence", "").startswith(("4", "5"))]
    elif filter_option == "BTST Setup":
        btst_data = [s for s in btst_data if s.get("Trend") == "BTST Setup"]

    if btst_data:
        render_trending_table(btst_data)
    else:
        st.warning("No trending stocks found at the moment.")

except Exception as e:
    st.error(f"⚠️ Error during scan: {e}")
