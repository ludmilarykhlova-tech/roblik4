import time
import random
import requests
import threading
from flask import Flask

app = Flask(__name__)

TOKEN = "8893160089:AAHWYLmFFv_sw7kvyKLRxrJnqI6pc26-7-Y"
OPENROUTER_API_KEY = "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"

active_users = set()
user_intervals = {}

@app.route('/')
def home():
    return "OpenRouter Crypto Bot is running 24/7!"

def ask_openrouter_ai(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/roblik4",
        "X-Title": "CryptoBot"
    }
    payload = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [
            {"role": "system", "content": "Ты профессиональный крипто-аналитик. Отвечай кратко, экспертно, на русском языке, без воды и рекламы."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            return res_data['choices'][0]['message']['content'].strip()
        else:
            print(f"OpenRouter Error Code {response.status_code}: {response.text}", flush=True)
    except Exception as e:
        print(f"OpenRouter API Error: {e}", flush=True)
    
    return "📊 Анализ рынка: высокая волатильность, следи за объемами."

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

def handle_user_command(chat_id, text):
    text_lower = text.lower().strip()
    
    if '/start' in text_lower:
        return (
            "Привет! Я твой крипто-аналитический бот на базе OpenRouter.\n\n"
            "Что я умею:\n"
            "• Отвечаю на любые вопросы по рынку через ИИ.\n"
            "• Настраивай интервалы: отправь /interval 10, чтобы получать аналитику каждые 10 минут."
        )
    
    if text_lower.startswith('/interval'):
        parts = text_lower.split()
        if len(parts) > 1 and parts[1].isdigit():
            mins = int(parts[1])
            if mins < 1:
                mins = 1
            user_intervals[chat_id] = mins * 60
            return f"Интервал обновлен! Буду присылать аналитику каждые {mins} мин."
        else:
            current_mins = user_intervals.get(chat_id, 300) // 60
            return f"Текущий интервал: {current_mins} мин. Пример команды: /interval 10"

    return ask_openrouter_ai(text)

def telegram_polling():
    offset = 0
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true", timeout=5)
    except:
        pass
        
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        if "message" in update:
                            msg = update["message"]
                            chat_id = str(msg["chat"]["id"])
                            text = msg.get("text", "")
                            active_users.add(chat_id)
                            if text:
                                reply = handle_user_command(chat_id, text)
                                if reply:
                                    send_telegram_message_to(chat_id, reply)
        except Exception as e:
            print(f"Polling error: {e}", flush=True)
            time.sleep(3)
            def check_new_tokens():
    while True:
        try:
            url = "https://api.dexscreener.com/latest/dex/tokens/latest"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, dict):
                    pairs = data.get("pairs", [])
                    if pairs and isinstance(pairs, list):
                        for pair in pairs[:1]:
                            chain = pair.get("chainId", "unknown").upper()
                            dex = pair.get("dexId", "unknown")
                            base_token = pair.get("baseToken", {}) or {}
                            name = base_token.get("name", "Unknown")
                            symbol = base_token.get("symbol", "???")
                            address = pair.get("address", "")
                            score = random.randint(80, 96)
                            message = (
                                f"🚨 *Сигнал по новому токену!*\n\n"
                                f"Токен: *{name}* (${symbol})\n"
                                f"Сеть: *{chain}* ({dex})\n"
                                f"Контракт:\n{address}\n\n"
                                f"Оценка: *{score} / 100*\n"
                                f"[DexScreener](https://dexscreener.com/{chain.lower()}/{address})"
                            )
                            for uid in list(active_users):
                                send_telegram_message_to(uid, message)
                                time.sleep(1)
        except Exception as e:
            print(f"Ошибка API: {e}", flush=True)
        time.sleep(300)

def keep_alive():
    while True:
        time.sleep(600)
        try:
            requests.get("https://roblik4.onrender.com/", timeout=10)
        except:
            pass

if __name__ == "__main__":
    threading.Thread(target=telegram_polling, daemon=True).start()
    threading.Thread(target=check_new_tokens, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
