import os
import requests

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Dhammaan liiskaaga coins-ka oo loo habeeyey qaab Binance symbols ah
COINS = [
    "RAREUSDT", "AMPUSDT", "QNTUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", 
    "XRPUSDT", "SOLUSDT", "TRXUSDT", "ZECUSDT", "DOGEUSDT", "LINKUSDT", 
    "XMRUSDT", "ADAUSDT", "XLMUSDT", "NEARUSDT", "BCHUSDT", "LTCUSDT", 
    "SUIUSDT", "AVAXUSDT", "HBARUSDT", "TAOUSDT", "CROUSDT", "DOTUSDT", 
    "WLDUSDT", "ICPUSDT", "ETCUSDT", "KASUSDT", "POLUSDT", "ARBUSDT", 
    "RENDERUSDT", "JUPUSDT", "ALGOUSDT", "KCSUSDT", "ORDIUSDT", "TIAUSDT", 
    "INJUSDT", "STXUSDT", "FETUSDT", "ARUSDT", "SEIUSDT", "MANTAUSDT", 
    "PYTHUSDT", "EIGENUSDT", "ZKUSDT", "GALAUSDT", "SANDUSDT", "MANAUSDT", 
    "CHZUSDT", "ENJUSDT", "OPUSDT", "GRTUSDT", "CFXUSDT", "AIOZUSDT", 
    "APEUSDT", "GRASSUSDT"
]

def check_market():
    message = "🟢 **Market Signal / Price Update**\n\n"
    
    for symbol in COINS:
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url)
            data = response.json()
            
            price = data.get('price')
            if price:
                clean_name = symbol.replace("USDT", "")
                message += f"🔹 **{clean_name}**: ${float(price):,.4f}\n"
        except Exception as e:
            print(f"Khalad ku yimid {symbol}: {e}")
            
    message += "\n*Bot-kaagu wuxuu si guul leh u baadhay liiskaaga!*"
    send_telegram_message(message)

def send_telegram_message(text):
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    check_market()
