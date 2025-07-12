import requests
import pandas as pd
import streamlit as st

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

        # Required initial call to establish cookies
        session.get("https://www.nseindia.com", timeout=5)

        response = session.get(url, timeout=5)
        data = response.json()

        stocks = [row["symbol"] for row in data["data"] if row.get("symbol")]
        return list(sorted(set(stocks)))

    except Exception as e:
        print(f"❌ Error fetching F&O list: {e}")
        return []
