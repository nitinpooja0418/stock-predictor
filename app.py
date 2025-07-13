import streamlit as st
import pandas as pd
from utils.advanced_btst_scanner import fetch_btst_candidates
from utils.nse_fno_scraper import get_fno_stocks  # fallback to .txt handled there
from component.trending_table import render_trending_table

# Streamlit config
st.set_page_config(page_title="Stock Scanner Dashboard", layout="wide")
st.title("📈 Intraday & BTST Stock Scanner")

# Controls
timeframe = st.selectbox("Select Timeframe", ["5m", "15m", "1h", "1d"], index=1)
min_cond = st.slider("Minimum Strategy Conditions to Qualify", 1, 5, 2)

# Fetch F&O stock list
fno_stocks = get_fno_stocks()
if not fno_stocks:
    st.error("❌ Failed to load stock list. Check `fno_stock_list.txt` in /data folder.")
    st.stop()

# Run scan
with st.spinner("🔍 Scanning stocks..."):
    result = fetch_btst_candidates(fno_stocks, timeframe=timeframe, min_conditions=min_cond)

# Display results
if result:
    st.success(f"✅ {len(result)} strong stock setups found.")
    render_trending_table(result)
else:
    st.warning("⚠️ No stock met the criteria.")
    if "skipped_stocks" in st.session_state:
        df_skipped = pd.DataFrame(st.session_state["skipped_stocks"]).sort_values("RSI", ascending=False)
        st.markdown("### 🔍 Top RSI Stocks (Skipped)")
        st.dataframe(df_skipped.head(10))

# Show logs
if "scan_logs" in st.session_state and st.checkbox("📄 Show Detailed Scan Logs"):
    st.markdown("### Debug Logs")
    st.text("\n".join(st.session_state["scan_logs"]))
