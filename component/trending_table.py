# components/trending_table.py

import streamlit as st
import pandas as pd

def render_trending_table(stocks_data):
    if not stocks_data:
        st.info("No trending stocks found at the moment.")
        return

    df = pd.DataFrame(stocks_data)

    def highlight_trend(row):
        color = {
            "Bullish": "background-color: #00640020;",
            "Bearish": "background-color: #8B000020;",
            "Sideways": "background-color: #80808020;",
            "BTST Setup": "background-color: #00008020;"
        }.get(row.get("Trend", ""), "")
        return [color] * len(row)

    styled_df = df.style.apply(highlight_trend, axis=1)

    st.markdown("### 📊 Trending Stocks")
    st.dataframe(styled_df, use_container_width=True)
