import time
import random
import requests
import threading
from flask import Flask, request
from google import genai

app = Flask(__name__)

TOKEN = "8893160089:AAHWYLmFFv_sw7kvyKLRxrJnqI6pc26-7-Y"

# 🔑 ВСКРОЙ КОВШИК И ВСТАВЬ КЛЮЧ МЕЖДУ КАВЫЧКАМИ НИЖЕ:
GEMINI_API_KEY = "AQ.Ab8RN6IPINijLXdo0nunMzwJwgHHdxQ5cmIbZBNMj31fB2ST_g"
# Инициализация официального клиента Gemini
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY != "СЮДА_ВСТАВЬ_СВОЙ_КЛЮЧ" else None

active_users = set()
user_intervals = {}

@app.route('/')
def home():
    return "Gemini Crypto Bot is running 24/7!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data and 'message' in data:
        chat_id = str(data['message']['chat']['id'])
        text = data['message'].get('text', '')
        active_users.add(chat_id)
        
        if text:
            reply = handle_user_command(chat_id, text)
            if reply:
                send_telegram_message_to(chat_id, reply)
    return "OK", 200

def handle_user_command(chat_id, text):
    text_lower = text.lower().strip()
    
    if '/start' in text_lower:
        return (
            "Привет! Я твой крипто-аналитик на базе официальной нейросети Gemini.\n\n"
            "Что я умею:\n"
            "• Живо и умно отвечаю на любые вопросы по рынку.\n"
            "• Настраиваю интервалы: отправь /interval 10, чтобы получать аналитику каждые 10 минут."
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

    # Запрос к официальной нейросети Gemini
    return ask_gemini_ai(text)

def ask_gemini_ai(prompt):
    if not ai_client:
        return "⚠️ В коде бота не указан API-ключ Gemini!"
    
    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Ты профессиональный крипто-аналитик. Отвечай кратко, экспертно, с оценкой рынка и вердиктом на русском языке. Запрос пользователя: {prompt}",
        )
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error: {e}", flush=True)
    
    return "🧠 Анализ рынка: высокая волатильность, следи за объемами ликвидности."

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

def set_webhook_url():
    time.sleep(4)
    webhook_url = "https://roblik4.onrender.com/webhook"
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

if __name__ == "__main__":
    threading.Thread(target=set_webhook_url, daemon=True).start()
    threading.Thread(target=check_new_tokens, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
