import os
import requests

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

message = "Salaan! Bot-kaagu wuxuu si guul leh uga shaqeeyay GitHub Actions!"
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, json=payload)
print(response.json())
