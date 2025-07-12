import streamlit as st
import pandas as pd

def render_trending_table(stocks_data):
    if not stocks_data:
        st.info("No trending stocks found at the moment.")
        return

    # Add Confidence + Chart URL
    for stock in stocks_data:
        if "Confidence" not in stock:
            score = stock["Reason"].count("+") + 1
            stock["Confidence"] = f"{score}/5"
        stock["Chart"] = f"[📈 View Chart](https://www.tradingview.com/chart/?symbol=NSE:{stock['Stock']})"

    df = pd.DataFrame(stocks_data)
    df = df[["Stock", "LTP", "% Change", "Trend", "Confidence", "Reason", "Chart"]]
    df = df.sort_values(by="Confidence", ascending=False)

    def highlight_confidence(row):
        score = int(row["Confidence"].split("/")[0])
        if score == 5:
            return ["background-color: #004d0020"] * len(row)
        elif score == 4:
            return ["background-color: #ffb70320"] * len(row)
        else:
            return [""] * len(row)

    styled_df = df.style.apply(highlight_confidence, axis=1)

    st.markdown("### ✅ High-Confidence BTST Option Picks")
    st.dataframe(styled_df, use_container_width=True, column_config={
        "Chart": st.column_config.LinkColumn("Chart")
    })
