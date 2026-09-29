import time
import random
import requests
import threading
from flask import Flask, request

app = Flask(__name__)

# Твой токен бота
TOKEN = "8893160089:AAHWYLmFFv_sw7kvyKLRxrJnqI6pc26-7-Y"

# Список пользователей, с которыми общался бот, чтобы присылать им аналитику
active_users = set()
active_users.add("5908091045") # Твой ID сразу по умолчанию

@app.route('/')
def home():
    return "Bot is running 24/7!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data and 'message' in data:
        chat_id = str(data['message']['chat']['id'])
        text = data['message'].get('text', '')
        
        # Запоминаем пользователя, чтобы слать ему сигналы в личку
        active_users.add(chat_id)
        
        reply = generate_ai_response(text)
        send_telegram_message_to(chat_id, reply)
    return "OK", 200

def generate_ai_response(text):
    text_lower = text.lower()
    
    if '/start' in text_lower:
        return (
            "Привет! Я твой крипто-аналитик.\n"
            "Я постоянно мониторю новые пулы ликвидности и присылаю сигналы.\n"
            "Спроси меня о чем угодно, например: *'Какая монета сейчас перспективная?'* или *'Стоит ли покупать новые токены?'*"
        )
    
    # Имитация «умного» ответа на любые свободные вопросы пользователя
    tokens_pool = ["IEH", "Soloween", "Apex", "NovaX", "Vertex"]
    chosen_token = random.choice(tokens_pool)
    score = random.randint(65, 94)
    
    if score > 80:
        recommendation = "Мощный приток ликвидности, выглядит перспективно для небольшого риска."
    elif score > 70:
        recommendation = "Умеренная активность, стоит понаблюдать за объемами торгов."
    else:
        recommendation = "Высокая волатильность и риски, лучше воздержаться от покупки."

    return (
        f"🧠 *Анализ запроса:* «{text}»\n\n"
        f"Проанализировав текущие блокчейн-данные, отмечу токен *{chosen_token}*.\n"
        f"Оценка потенциала: *{score} / 100*\n"
        f"Вердикт ИИ: {recommendation}"
    )

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
                for pair in pairs[:1]:
                    chain = pair.get("chainId", "unknown").upper()
                    dex = pair.get("dexId", "unknown")
                    base_token = pair.get("baseToken", {})
                    name = base_token.get("name", "Unknown")
                    symbol = base_token.get("symbol", "???")
                    address = pair.get("address", "")
                    
                    score = random.randint(80, 96)
                    
                    message = (
                        f"*🤖 ИИ-Сигнал по новому токену!*\n\n"
                        f"Токен: *{name}* (${symbol})\n"
                        f"Сеть: *{chain}* ({dex})\n"
                        f"Контракт:\n{address}\n\n"
                        f"Оценка алгоритма: *{score} / 100*\n"
                        f"[DexScreener](https://dexscreener.com/{chain.lower()}/{address})"
                    )
                    
                    # Рассылаем всем активным пользователям (включая тебя)
                    for uid in active_users:
                        send_telegram_message_to(uid, message)
        except Exception as e:
            print(f"Ошибка API: {e}", flush=True)
            
        time.sleep(300)
        def keep_alive():
            """Пинг собственного сервера раз в 10 минут, чтобы Render не засыпал при закрытом ноутбуке"""
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
