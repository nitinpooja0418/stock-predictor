import streamlit as st
import requests
import time
import os

@st.cache_data(ttl=3600)
def get_fno_stocks():
    try:
        url = "https://www.nseindia.com/api/liveEquity-derivatives?index=stock_fut"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nseindia.com/"
        }

        session = requests.Session()
        session.headers.update(headers)
        session.get("https://www.nseindia.com", timeout=5)
        time.sleep(1)

        response = session.get(url, timeout=5)
        data = response.json()

        stocks = [row["symbol"] for row in data["data"] if row.get("symbol")]
        return sorted(list(set(stocks)))

    except Exception as e:
        print(f"⚠️ NSE fetch error: {e}")
        # Fallback to local stock list
        try:
            with open("data/fno_stock_list.txt", "r") as file:
                fallback_stocks = [line.strip() for line in file if line.strip()]
                return fallback_stocks
        except Exception as fe:
            print(f"⚠️ Fallback failed: {fe}")
            return []
