import requests

BOT_TOKEN = "8306289273:AAFTgnAjaqk7LJxEEdepOaRxQ6k_ENRKQs8"
CHAT_ID = "1084170827"

def send_telegram(message):
    url = f"https://api.telegram.org/bot8306289273:AAFTgnAjaqk7LJxEEdepOaRxQ6k_ENRKQs8/sendMessage"
    payload = {"chat_id": 1084170827, "text": message}
    requests.post(url, data=payload)

send_telegram("Hello! Telegram alerts are working ✅")
