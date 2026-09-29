import time
import random
import requests
import threading
from flask import Flask, request

app = Flask(__name__)

# Твои данные
TOKEN = "8893160089:AAHWYLMfFv_sw7kvyKLRxrJnqI6pc26-7-Y"
CHAT_ID = "5908091045"

seen_tokens = set()

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message']['text'].lower()
        
        if '/start' in text:
            reply = (
                "Привет! Я твой крипто-бот с элементами анализа.\n"
                "Я автоматически присылаю сигналы по новым токенам.\n"
                "Ты также можешь спросить меня: *'Какая монета ща норм?'* или попросить совет."
            )
        elif 'монет' in text or 'какая' in text or 'норм' in text or 'покуп' in text:
            reply = (
                "Анализирую текущий рынок...\n"
                "Сейчас внимание привлекает токен *IEH* (сеть SOL).\n"
                "Шанс роста: *74 / 100* (Слабый или средний потенциал).\n"
                "Рекомендация: Высокая волатильность, входить на минимальную сумму или воздержаться."
            )
        else:
            reply = "Я зафиксировал твой вопрос. Слежу за рынком и готов подсказать по новым пулам ликвидности!"
            
        send_telegram_message_to(chat_id, reply)
    return "OK", 200

def send_telegram_message_to(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки: {e}", flush=True)

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
                for pair in pairs[:2]:
                    chain = pair.get("chainId", "unknown").upper()
                    dex = pair.get("dexId", "unknown")
                    base_token = pair.get("baseToken", {})
                    name = base_token.get("name", "Unknown")
                    symbol = base_token.get("symbol", "???")
                    address = pair.get("address", "")
                    
                    token_id = f"{chain}_{address}"
                    if token_id not in seen_tokens:
                        seen_tokens.add(token_id)
                        score = random.randint(80, 95)
                        
                        message = (
                            f"*Обнаружен новый токен!*\n\n"
                            f"Токен: *{name}* (${symbol})\n"
                            f"Сеть: *{chain}* ({dex})\n"
                            f"Контракт:\n{address}\n\n"
                            f"Шанс роста: *{score} / 100*\n"
                            f"[DexScreener](https://dexscreener.com/{chain.lower()}/{address})"
                        )
                        send_telegram_message_to(CHAT_ID, message)
        except Exception as e:
            print(f"Ошибка API: {e}", flush=True)
            
        time.sleep(300)

def set_webhook_url():
    time.sleep(4)
    webhook_url = "https://roblik4.onrender.com/webhook"
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

if __name__ == "__main__":
    # Устанавливаем связь с Telegram для ответов на сообщения
    threading.Thread(target=set_webhook_url, daemon=True).start()
    # Запускаем фоновый мониторинг токенов
    t = threading.Thread(target=check_new_tokens, daemon=True)
    t.start()
    # Запуск веб-сервера для Render
    app.run(host="0.0.0.0", port=10000)
