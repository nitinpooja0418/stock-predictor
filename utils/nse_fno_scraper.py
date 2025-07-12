import streamlit as st
import requests
import time

@st.cache_data(ttl=3600)
def get_fno_stocks():
    try:
        url = "https://www.nseindia.com/api/liveEquity-derivatives?index=stock_fut"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/"
        }

        session = requests.Session()
        session.headers.update(headers)

        # Initial request to get cookies
        session.get("https://www.nseindia.com", timeout=5)
        time.sleep(1)  # Wait 1 sec

        response = session.get(url, timeout=5)
        data = response.json()

        stocks = [row["symbol"] for row in data["data"] if row.get("symbol")]
        return sorted(list(set(stocks)))

    except Exception as e:
        print(f"❌ NSE fetch error: {e}")
        return []
