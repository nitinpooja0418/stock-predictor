import streamlit as st
from predictor.model import predict_stock_move
from watchlist.config import stock_list
from utils.helpers import get_signal_strength
from telegram_bot.bot import send_telegram_signal

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
