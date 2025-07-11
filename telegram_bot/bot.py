import requests

# Replace these with your bot's details
TELEGRAM_BOT_TOKEN = "7353581286:AAG6FvyRCVvwFZmHbw5ZYRiHux7KqbwXHA0"
TELEGRAM_CHAT_ID = "1057590354"

def send_telegram_signal(symbol, signal, confidence, timeframe):
    """
    Sends a signal to your Telegram channel/chat.
    """
    message = (
        f"📊 AI Stock Predictor Signal\n"
        f"🧾 Stock: {symbol}\n"
        f"⏱️ Timeframe: {timeframe}\n"
        f"📈 Signal: {signal.upper()}\n"
        f"🔐 Confidence: {confidence}%"
    )

    url = (
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
        f"/sendMessage?chat_id={TELEGRAM_CHAT_ID}"
        f"&text={message}&parse_mode=Markdown"
    )

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Telegram signal sent successfully.")
        else:
            print("Telegram error:", response.text)
    except Exception as e:
        print("Telegram exception:", e)
