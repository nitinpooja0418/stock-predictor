import streamlit as st
from predictor.model import predict_stock_move
from watchlist.config import stock_list
from utils.helpers import get_signal_strength
from telegram_bot.bot import send_telegram_signal

from component.trending_table import render_trending_table
from component.tradingview_chart import display_tradingview_chart

# 📌 Choose timeframe
timeframe_map = {
    "1 Minute": "1",
    "5 Minutes": "5",
    "15 Minutes": "15",
    "1 Hour": "60",
    "Daily": "D"
}
selected_tf = st.sidebar.selectbox("Select Timeframe", list(timeframe_map.keys()))
tv_interval = timeframe_map[selected_tf]

# 📊 Sample Trending Data (replace this with real logic later)
stocks_data = [
    {"Stock": "RELIANCE", "Change %": 1.45, "Trend": "Bullish", "Reason": "Breakout above resistance"},
    {"Stock": "ICICIBANK", "Change %": -0.82, "Trend": "Bearish", "Reason": "Breakdown with volume"},
    {"Stock": "ITC", "Change %": 0.05, "Trend": "Sideways", "Reason": "Low volatility range"},
]

# 📋 Render table + show TradingView chart
watchlist = render_trending_table(stocks_data, selected_tf)
selected_stock = st.selectbox("📈 Select stock for live chart", watchlist)
display_tradingview_chart(selected_stock, tv_interval)

st.set_page_config(page_title="AI Stock Predictor", layout="wide")

st.title("📈 AI Stock Predictor – LSTM + Price Action")
selected_stock = st.selectbox("Select a stock:", stock_list)
selected_timeframe = st.selectbox("Select timeframe:", ["5min", "15min", "Daily"])

if st.button("Predict"):
    with st.spinner("Predicting..."):
        result = predict_stock_move(selected_stock, selected_timeframe)
        signal = result['signal']
        confidence = get_signal_strength(result)

        st.subheader(f"Prediction: {signal.upper()}")
        st.progress(confidence / 100)
        st.write(f"Confidence: {confidence}%")

        if st.checkbox("Send signal to Telegram"):
            send_telegram_signal(selected_stock, signal, confidence, timeframe=selected_timeframe)


from utils.nse_scanner import fetch_breakout_candidates

candidates = fetch_breakout_candidates()

for stock_data in candidates:
    stock = stock_data["Stock"]
    ltp = stock_data["LTP"]
    change = stock_data["% Change"]

    trend, reason = get_trend_prediction(stock)  # Your prediction logic

    trending_data.append({
        "Stock": stock,
        "LTP": ltp,
        "% Change": change,
        "Trend": trend,
        "Reason": reason
    })

render_trending_table(trending_data)



from utils.advanced_btst_scanner import fetch_btst_candidates

fno_stocks = fetch_fno_list()  # From previous module
btst_setups = fetch_btst_candidates(fno_stocks)

trending_data = []

for stock_data in btst_setups:
    trending_data.append({
        "Stock": stock_data["Stock"],
        "LTP": stock_data["LTP"],
        "% Change": "-",  # you can fetch separately if needed
        "Trend": stock_data["Trend"],
        "Reason": stock_data["Reason"]
    })

render_trending_table(trending_data)
