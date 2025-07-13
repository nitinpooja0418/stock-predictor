def fetch_btst_candidates(stock_list, timeframe="15m", test_mode=False, scan_type="BTST"):
    btst_stocks = []

    for symbol in stock_list:
        try:
            df = yf.download(f"{symbol}.NS", period="5d", interval=timeframe, progress=False)

            if df.empty or len(df) < 20:
                continue

            required_cols = ['Close', 'High', 'Volume']
            if not all(col in df.columns for col in required_cols):
                print(f"❌ Error with {symbol}: Missing columns {required_cols}")
                continue

            df.dropna(subset=required_cols, inplace=True)

            # Indicators
            df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
            df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()
            macd = MACD(close=df["Close"])
            df["MACD"] = macd.macd_diff()

            last = df.iloc[-1]
            prev = df.iloc[-2]

            reason = []

            # Common condition
            if last["Close"] > last["EMA20"] and last["Volume"] > prev["Volume"] * 1.5:
                reason.append("Above EMA20 + Volume Spike")

            if scan_type == "BTST":
                if last["RSI"] > 60:
                    reason.append("Strong RSI")
                if last["Close"] > df["High"].rolling(10).max().iloc[-2]:
                    reason.append("10-Bar High Breakout")
                if last["MACD"] > 0:
                    reason.append("MACD Bullish Crossover")

            elif scan_type == "Intraday":
                if last["RSI"] > 65:
                    reason.append("Overbought RSI (Momentum)")
                if last["MACD"] > 0 and prev["MACD"] < 0:
                    reason.append("MACD Crossover Just Happened")
                if last["Close"] > df["High"].rolling(5).mean().iloc[-2]:
                    reason.append("Above 5-bar avg high")

            if len(reason) >= 2:
                btst_stocks.append({
                    "Stock": symbol,
                    "Close": round(last["Close"], 2),
                    "Trend": f"{scan_type} Setup",
                    "Confidence": f"{len(reason)}/5",
                    "Reason": ", ".join(reason),
                    "LTP": round(last["Close"], 2),
                    "TradingView": f"https://in.tradingview.com/symbols/NSE-{symbol}/"
                })

        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")
            continue

    return btst_stocks
