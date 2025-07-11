# utils/nse_scanner.py

import requests
import pandas as pd
import time

def fetch_fno_list():
    # Static list of top F&O stocks (can be expanded)
    return [
        "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "SBIN",
        "ITC", "AXISBANK", "LT", "KOTAKBANK", "HINDUNILVR", "BAJFINANCE",
        "MARUTI", "ASIANPAINT", "HCLTECH", "POWERGRID", "ULTRACEMCO"
    ]

def fetch_breakout_candidates():
    url = "https://www.nseindia.com/market-data/top-gainers"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com"
    }

    session = requests.Session()
    try:
        # Initial session hit
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        time.sleep(1)

        response = session.get(url, headers=headers, timeout=5)
        tables = pd.read_html(response.text)

        if tables:
            df = tables[0]
            df.columns = [col.strip() for col in df.columns]

            # Filter logic
            df = df[df['% Change'] > 2.0]
            df = df[df['Volume'] > 1000000]
            fno_stocks = fetch_fno_list()
            df = df[df['Symbol'].isin(fno_stocks)]

            return df[['Symbol', 'LTP (Rs.)', '% Change']].rename(
                columns={"Symbol": "Stock", "LTP (Rs.)": "LTP"}
            ).to_dict(orient='records')

    except Exception as e:
        print("Error fetching from NSE:", e)

    return []
