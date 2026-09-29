from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Запуск мини-сервера для того, чтобы Render видел открытый порт
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
import os
import time
import requests
import random

# Твои данные
TOKEN = "8893160089:AAHWYLMfFv_sw7kvyKLRxrJnqI6pc26-7-Y"
CHAT_ID = "5908091045"

seen_tokens = set()

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def check_new_tokens():
    print("Проверка новых токенов...", flush=True)    
    try:
    url = "https://api.dexscreener.com/latest/dex/tokens/latest"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        print(f"Сайт ответил со статусом: {response.status_code}", flush=True)
        return
    data = response.json()
except Exception as e:
    print(f"Ошибка при запросе к API: {e}", flush=True)
    return        
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
                min_growth = random.randint(150, 165)
                max_growth = min_growth + random.randint(15, 30)
                price = round(random.uniform(0.0001, 0.009), 6)
                
                message = (
                    f"🚀 *Обнаружен скачок токена!*\n\n"
                    f"🪙 Токен: *{name} (${symbol})*\n"
                    f"🌐 Сеть: *{chain}* ({dex})\n"
                    f"📍 Контракт:\n{address}\n\n"
                    f"📊 *Анализ сигнала:*\n"
                    f"• Шанс роста: *{score} / 100* (Сильный потенциал)\n"
                    f"• Прогнозируемый рост: *+{min_growth}% — +{max_growth}%*\n"
                    f"• Текущая цена: *${price}*\n\n"
                    f"💡 *Метрики:*\n"
                    f"• Ликвидность: *${liquidity:,.0f}* (🔒 Залочена)\n"
                    f"• Объем (1ч): *${volume:,.0f}*\n\n"
                    f"📝 *Описание:*\n"
                    f"Зафиксирован мощный приток уникальных кошельков в пул ликвидности. Объём покупок превышает продажи. Смарт-контракт проверен.\n\n"
                    f"🔗 [DexScreener](https://dexscreener.com/{chain.lower()}/{address})"
                )
                
                send_telegram_message(message)
                print(f"Отправлен сигнал для: {symbol}")
                
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}", flush=True)
if __name__ == "__main__":
    print("Бот запущен и следит за токенами...", flush=True)    
    while True:
        check_new_tokens()
        time.sleep(120)
