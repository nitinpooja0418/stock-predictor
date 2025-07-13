import os
import requests

# Path to your offline stock list
FNO_FILE_PATH = os.path.join("data", "fno_stock_list.txt")

def get_fno_stocks():
    try:
        # Attempt to fetch live F&O stocks from NSE API
        url = "https://www.nseindia.com/api/liveEquity-derivatives"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nseindia.com"
        }

        with requests.Session() as s:
            s.headers.update(headers)
            response = s.get(url, timeout=5)
            data = response.json()

            symbols = list(set(item["symbol"] for item in data["data"]))
            if symbols:
                return sorted(symbols)

    except Exception as e:
        print(f"[Fallback] Using offline F&O stock list. Error: {e}")

    # Load from fallback text file
    if os.path.exists(FNO_FILE_PATH):
        with open(FNO_FILE_PATH, "r") as f:
            return sorted(list(set(line.strip().upper() for line in f if line.strip())))
    else:
        print("❌ Offline F&O file not found at data/fno_stock_list.txt")
        return []
