import streamlit as st
import pandas as pd
from utils.nse_fno_scraper import get_fno_stocks
from utils.advanced_btst_scanner import fetch_btst_candidates
from component.trending_table import render_trending_table

# Page setup
st.set_page_config(page_title="Stock Trend Dashboard", layout="wide")
st.title("📈 AI Stock Trend & BTST Dashboard")

# -------------------------------
# UI Controls
# -------------------------------
timeframe = st.selectbox("⏱️ Select Timeframe", ["5m", "15m", "1h", "1d"], index=1)

scan_type = st.radio("🧠 Select Strategy Type", ["BTST", "Intraday"], horizontal=True)

filter_option = st.selectbox("📊 Filter by Confidence / Trend", [
    "All", "Only 5/5", "4/5+", "BTST Setup", "Intraday Setup"
])

single_stock = st.text_input("🔍 Enter single stock symbol (optional)", placeholder="e.g. RELIANCE")

# -------------------------------
# Run Scanner
# -------------------------------
if st.button("🚀 Run Scanner"):
    with st.spinner("🔍 Scanning stock(s) for potential setup..."):

        if single_stock:
            stock_list = [single_stock.upper()]
            test_mode = True
        else:
            fno_stocks = get_fno_stocks()
            if not fno_stocks:
                st.error("❌ Failed to load F&O stock list.")
                st.stop()
            stock_list = fno_stocks
            test_mode = False

        try:
            btst_data = fetch_btst_candidates(
                stock_list,
                timeframe=timeframe,
                test_mode=test_mode,
                scan_type=scan_type
            )

            # Filter logic
            if filter_option == "Only 5/5":
                btst_data = [s for s in btst_data if s.get("Confidence", "").startswith("5")]
            elif filter_option == "4/5+":
                btst_data = [s for s in btst_data if s.get("Confidence", "").startswith(("4", "5"))]
            elif filter_option == "BTST Setup":
                btst_data = [s for s in btst_data if s.get("Trend") == "BTST Setup"]
            elif filter_option == "Intraday Setup":
                btst_data = [s for s in btst_data if s.get("Trend") == "Intraday Setup"]

            if btst_data:
                st.success(f"✅ {len(btst_data)} stock(s) found with valid {scan_type} setup.")
                render_trending_table(btst_data)
            else:
                st.warning(f"No valid {scan_type} setups found.")

        except Exception as e:
            st.error(f"⚠️ Error during scanning: {e}")
