def fetch_btst_candidates(stock_list, timeframe="15m", min_conditions=2, test_mode=False):
    import yfinance as yf
    from ta.trend import EMAIndicator, MACD
    from ta.momentum import RSIIndicator

    btst_stocks = []
    skipped_stocks = []
    scan_logs = []

    for symbol in stock_list:
        try:
            df = yf.download(symbol + ".NS", period="5d", interval=timeframe, progress=False)

            if df.empty or len(df) < 30:
                scan_logs.append(f"⚠️ {symbol}: Insufficient data ({len(df)} rows)")
                continue

            df.dropna(inplace=True)

            required_cols = ["Close", "Volume", "High"]
            if not all(col in df.columns for col in required_cols):
                scan_logs.append(f"⚠️ {symbol}: Missing columns {required_cols}")
                continue

            # Indicators
            df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
            df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()
            macd = MACD(close=df["Close"])
            df["MACD"] = macd.macd()
            df["MACD_signal"] = macd.macd_signal()

            df.dropna(inplace=True)
            if len(df) < 10:
                scan_logs.append(f"⚠️ {symbol}: Not enough rows after indicator calc")
                continue

            last = df.iloc[-1]
            prev = df.iloc[-2]
            reasons = []

            # Scalar-safe comparisons
            close = float(last["Close"])
            ema20 = float(last["EMA20"])
            volume = float(last["Volume"])
            prev_volume = float(prev["Volume"])
            macd_val = float(last["MACD"])
            macd_signal = float(last["MACD_signal"])
            rsi = float(last["RSI"])

            # Conditions
            if close > ema20:
                reasons.append("Above EMA20")

            if volume > prev_volume * 1.5:
                reasons.append("Volume Spike")

            if macd_val > macd_signal:
                reasons.append("MACD Bullish Crossover")

            if rsi > 55:
                reasons.append(f"RSI Strong ({round(rsi, 1)})")

            try:
                rolling_high = float(df["High"].rolling(10).max().iloc[-2])
                if close > rolling_high:
                    reasons.append("10-Bar High Breakout")
            except Exception as e:
                scan_logs.append(f"⚠️ {symbol}: Failed high breakout calc: {e}")

            # Decision
            if len(reasons) >= min_conditions:
                trend_type = "BTST Setup" if timeframe in ["15m", "1d"] else "Intraday Setup"
                btst_stocks.append({
                    "Stock": symbol,
                    "Close": round(close, 2),
                    "Trend": trend_type,
                    "Confidence": f"{len(reasons)}/5",
                    "Reason": ", ".join(reasons),
                    "LTP": round(close, 2),
                    "TradingView": f"https://in.tradingview.com/symbols/NSE-{symbol}/"
                })
            else:
                skipped_stocks.append({"Stock": symbol, "RSI": round(rsi, 1)})
        except Exception as e:
            scan_logs.append(f"⚠️ {symbol}: {e}")
            continue

    if not test_mode:
        st.session_state["skipped_stocks"] = skipped_stocks
        st.session_state["scan_logs"] = scan_logs

    return btst_stocks
