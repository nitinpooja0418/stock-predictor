import streamlit as st
from utils.nse_fno_scraper import get_fno_stocks

st.set_page_config(page_title="Stock Trend Dashboard", layout="wide")
st.markdown("## 📈 Trending Stock Analysis (BTST + Breakout)")

timeframe = st.selectbox("Select Timeframe", ["5m", "15m", "Daily"])
filter_option = st.selectbox("Filter by Confidence / Trend", [
    "All", "Only 5/5", "4/5+", "BTST Setup"
])

# Show spinner while fetching F&O list
with st.spinner("Fetching live F&O stock list from NSE..."):
    fno_stocks = get_fno_stocks()

if not fno_stocks:
    st.error("❌ Failed to load F&O stock list. Please retry later.")
else:
    try:
        from utils.advanced_btst_scanner import fetch_btst_candidates
        from component.trending_table import render_trending_table

        trending_data = fetch_btst_candidates(fno_stocks)

        if filter_option == "Only 5/5":
            trending_data = [s for s in trending_data if s.get("Confidence", "").startswith("5")]
        elif filter_option == "4/5+":
            trending_data = [s for s in trending_data if s.get("Confidence", "").startswith(("4", "5"))]
        elif filter_option == "BTST Setup":
            trending_data = [s for s in trending_data if s.get("Trend") == "BTST Setup"]

        render_trending_table(trending_data)

    except Exception as e:
        st.error(f"⚠️ Error while scanning stocks: {e}")
