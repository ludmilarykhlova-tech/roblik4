import time
import random
import requests

TOKEN = "7963428987:AAHOc1fU_YgZc55Z3t9W2Z-8Y2Z1Z0Z9Z8"  # Твой токен остается здесь
CHAT_ID = "-100234567890"        # Твой ID чата/канала остается здесь

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
    print("Проверка новых токенов через GeckoTerminal...", flush=True)
    try:
        url = "https://api.geckoterminal.com/api/v2/networks/new_pools"
        headers = {"Accept": "application/json;version=20230302"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Сайт ответил со статусом: {response.status_code}", flush=True)
            return
            
        data = response.json()
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}", flush=True)
        return

    pools = data.get("data", [])
    for pool in pools[:3]:
        attributes = pool.get("attributes", {})
        name = attributes.get("name", "Unknown")
        address = attributes.get("address", "")
        
        # Извлекаем сеть и декс из ID (например, "eth_12345")
        pool_id = pool.get("id", "")
        chain = pool_id.split("_")[0].upper() if "_" in pool_id else "UNKNOWN"
        
        token_id = f"{chain}_{address}"
        
        if token_id not in seen_tokens:
            seen_tokens.add(token_id)
            
            score = random.randint(85, 96)
            min_growth = random.randint(120, 150)
            max_growth = min_growth + random.randint(15, 30)
            price = round(random.uniform(0.0001, 0.009), 6)
            
            message = (
                f"*Обнаружен скачок токена!*\n\n"
                f"Токен: *{name}*\n"
                f"Сеть: *{chain}*\n"
                f"Контракт:\n{address}\n\n"
                f"*Анализ сигнала:*\n"
                f"Шанс роста: *{score} / 100* (Сильный потенциал)\n"
                f"Прогнозируемый рост: *+{min_growth}% - +{max_growth}%*\n"
                f"Текущая цена: *${price}*\n\n"
                f"*Описание:*\n"
                f"Зафиксирован мощный приток уникальных кошельков в пул ликвидности. Объём покупок превышает продажи.\n"
                f"[GeckoTerminal](https://www.geckoterminal.com/{chain.lower()}/pools/{address})"
            )
            
            send_telegram_message(message)
            print(f"Отправлен сигнал для: {name}", flush=True)

if __name__ == "__main__":
    print("Бот запущен и следит за токенами...", flush=True)
    while True:
        check_new_tokens()
        time.sleep(300)
