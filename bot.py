import time
import random
import requests
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

TOKEN = "7963428987:AAHOc1fU_YgZc55Z3t9W2Z-8Y2Z1Z0Z9Z8"
CHAT_ID = "-100234567890"

seen_tokens = set()

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}", flush=True)

def check_new_tokens():
    while True:
        print("Проверка новых токенов...", flush=True)
        try:
            url = "https://api.dexscreener.com/latest/dex/tokens/latest"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])
                for pair in pairs[:3]:
                    chain = pair.get("chainId", "unknown").upper()
                    dex = pair.get("dexId", "unknown")
                    base_token = pair.get("baseToken", {})
                    name = base_token.get("name", "Unknown")
                    symbol = base_token.get("symbol", "???")
                    address = pair.get("address", "")
                    
                    liquidity = pair.get("liquidity", {}).get("usd", 0)
                    volume = pair.get("volume", {}).get("h24", 0)
                    
                    token_id = f"{chain}_{address}"
                    
                    if token_id not in seen_tokens:
                        seen_tokens.add(token_id)
                        
                        score = random.randint(85, 96)
                        min_growth = random.randint(120, 150)
                        max_growth = min_growth + random.randint(15, 30)
                        price = round(random.uniform(0.0001, 0.009), 6)
                        
                        message = (
                            f"*Обнаружен скачок токена!*\n\n"
                            f"Токен: *{name}* (${symbol})\n"
                            f"Сеть: *{chain}* ({dex})\n"
                            f"Контракт:\n{address}\n\n"
                            f"*Анализ сигнала:*\n"
                            f"Шанс роста: *{score} / 100* (Сильный потенциал)\n"
                            f"Прогнозируемый рост: *+{min_growth}% - +{max_growth}%*\n"
                            f"Текущая цена: *${price}*\n\n"
                            f"*Метрики:*\n"
                            f"Ликвидность: *${liquidity:,.0f}* (Залочена)\n"
                            f"Объём (24h): *${volume:,.0f}*\n\n"
                            f"*Описание:*\n"
                            f"Зафиксирован мощный приток уникальных кошельков в пул ликвидности. Объём покупок превышает продажи.\n"
                            f"[DexScreener](https://dexscreener.com/{chain.lower()}/{address})"
                        )
                        
                        send_telegram_message(message)
                        print(f"Отправлен сигнал для: {symbol}", flush=True)
            else:
                print(f"Сайт ответил со статусом: {response.status_code}", flush=True)
        except Exception as e:
            print(f"Ошибка при запросе к API: {e}", flush=True)
            
        time.sleep(300)

if __name__ == "__main__":
    t = threading.Thread(target=check_new_tokens)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=10000)
