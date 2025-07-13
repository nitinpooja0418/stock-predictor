import streamlit as st
import pandas as pd
from utils.advanced_btst_scanner import fetch_btst_candidates
from component.trending_table import render_trending_table

# Streamlit page config
st.set_page_config(page_title="📈 Stock Trend & BTST Scanner", layout="wide")
st.title("📊 AI-Based Stock Scanner (Intraday & BTST)")

# UI Elements
timeframe = st.selectbox("🕒 Timeframe", ["5m", "15m", "1d"], index=1)
min_conditions = st.slider("🧠 Minimum Conditions to Qualify", 1, 5, 2)
show_skipped = st.checkbox("🔎 Show Skipped Stocks (Top by RSI)", value=True)

# Load F&O stock list from offline file
@st.cache_data
def load_stock_list():
    try:
        with open("data/fno_stock_list.txt", "r") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except Exception as e:
        st.error(f"Failed to load stock list: {e}")
        return []

stock_list = load_stock_list()

if not stock_list:
    st.stop()

# Run the Scanner
with st.spinner("🚀 Scanning stocks for valid setups..."):
    results = fetch_btst_candidates(
        stock_list, 
        timeframe=timeframe, 
        min_conditions=min_conditions,
        test_mode=False
    )

# Display Results
if results:
    st.success(f"✅ {len(results)} stocks matched criteria")
    render_trending_table(results)
else:
    st.warning("⚠️ No strong stock setups found. Try lowering minimum conditions or changing timeframe.")

# Optional: Show Skipped Stocks Sorted by RSI
if show_skipped and "skipped_stocks" in st.session_state:
    skipped = st.session_state["skipped_stocks"]
    if skipped:
        df_skipped = pd.DataFrame(skipped)
        if "RSI" in df_skipped.columns:
            df_skipped = df_skipped.sort_values("RSI", ascending=False)
            st.markdown("### 🔍 Top RSI Stocks (Skipped)")
            st.dataframe(df_skipped.head(10), use_container_width=True)
        else:
            st.info("No RSI data available for skipped stocks.")
    else:
        st.info("No skipped stocks recorded.")

# Optional: Show Logs
if "scan_logs" in st.session_state and st.session_state["scan_logs"]:
    with st.expande
