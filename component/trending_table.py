import streamlit as st
import pandas as pd

def render_trending_table(stocks_data):
    if not stocks_data:
        st.info("No trending stocks found at the moment.")
        return

    for stock in stocks_data:
        # Ensure Chart URL is present
        stock["Chart"] = f"[📈 View Chart](https://www.tradingview.com/chart/?symbol=NSE:{stock['Stock']})"

    # Build DataFrame
    df = pd.DataFrame(stocks_data)

    # Handle missing optional columns gracefully
    required_cols = ["Stock", "LTP", "Trend", "Confidence", "Reason", "Chart"]
    df = df[[col for col in required_cols if col in df.columns]]

    # Sort by confidence score (e.g., "3/4" => 3)
    if "Confidence" in df.columns:
        df["ConfScore"] = df["Confidence"].apply(lambda x: int(str(x).split("/")[0]))
        df = df.sort_values(by="ConfScore", ascending=False)
        df.drop(columns=["ConfScore"], inplace=True)

    def highlight_confidence(row):
        try:
            score = int(str(row["Confidence"]).split("/")[0])
        except:
            score = 0
        if score == 4:
            return ["background-color: #004d0020"] * len(row)
        elif score == 3:
            return ["background-color: #ffb70320"] * len(row)
        else:
            return [""] * len(row)

    styled_df = df.style.apply(highlight_confidence, axis=1)

    st.markdown("### ✅ High-Confidence BTST Picks")
    st.dataframe(
        styled_df,
        use_container_width=True,
        column_config={
            "Chart": st.column_config.LinkColumn("Chart")
        }
    )
