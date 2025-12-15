import telebot
import threading
import time
import datetime
import re
from flask import Flask
import os

TOKEN = '8400022159:AAH5pQcA8hziNto4keJ4xMe9-TP6yAGx-0c'

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот живой! 🐍", 200

# Фоновый поток для веб-сервера (Render требует, чтобы был HTTP)
def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# Список напоминаний
reminders = []

def schedule_reminders():
    while True:
        now = time.time()
        to_remove = []
        for i, (chat_id, text, remind_time) in enumerate(reminders):
            if now >= remind_time:
                bot.send_message(chat_id, f"🔔 Напоминание: {text}")
                to_remove.append(i)
        for i in reversed(to_remove):
            reminders.pop(i)
        time.sleep(1)

threading.Thread(target=schedule_reminders, daemon=True).start()

# Запускаем Flask в отдельном потоке (не блокирует polling)
threading.Thread(target=run_flask, daemon=True).start()

# Обработчики бота (те же, что были)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой бот на Python 🐍\nЖивой и вечный!\n/help — меню")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "🔹 /start — приветствие\n"
                          "🔹 Напиши математику — посчитаю\n"
                          "🔹 Напиши «напомни [что] через/в [время]» — напомню\n"
                          "Примеры: напомни попить воды через 5 минут")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    text = message.text.strip()

    if text.lower().startswith('напомни '):
        parse_reminder(message)
        return

    try:
        result = eval(text)
        bot.reply_to(message, f"🔢 Результат: {result}")
        return
    except:
        pass

    bot.reply_to(message, f"💬 Ты написал: {text}")

# Парсер напоминаний (тот же)
def parse_reminder(message):
    original_text = message.text
    chat_id = message.chat.id
    lower_text = original_text.lower()

    if ' через ' in lower_text:
        parts = original_text.split(' через ', 1)
        reminder_text = parts[0].replace('напомни ', '').replace('Напомни ', '').strip()
        time_str = parts[1].strip()
        delay = parse_relative_time(time_str)
    elif ' в ' in lower_text:
        parts = original_text.split(' в ', 1)
        reminder_text = parts[0].replace('напомни ', '').replace('Напомни ', '').strip()
        time_str = parts[1].strip()
        delay = parse_absolute_time(time_str)
    else:
        bot.reply_to(message, "Используй «через» или «в»")
        return

    if delay is None or delay <= 0:
        bot.reply_to(message, "Не понял время 😔")
        return

    remind_time = time.time() + delay
    reminders.append((chat_id, reminder_text, remind_time))
    bot.reply_to(message, f"✅ Напомню «{reminder_text}» через {format_time(delay)}")

# Функции парсинга (оставь как были)
def parse_relative_time(time_str):
    # ... (тот же код, что был раньше)
    time_str = time_str.lower()
    minutes = 0
    hours = 0
    days = 0
    match = re.search(r'(\d+)\s*(день|дня|дней)', time_str)
    if match: days = int(match.group(1))
    match = re.search(r'(\d+)\s*(час|часа|часов)', time_str)
    if match: hours = int(match.group(1))
    match = re.search(r'(\d+)\s*(минут|минуты|минута)', time_str)
    if match: minutes = int(match.group(1))
    total = days * 86400 + hours * 3600 + minutes * 60
    return total if total > 0 else None

def parse_absolute_time(time_str):
    # ... (тот же)
    time_str = time_str.lower()
    now = datetime.datetime.now()
    if 'завтра' in time_str:
        now += datetime.timedelta(days=1)
        time_str = time_str.replace('завтра', '').strip()
    match = re.search(r'(\d{1,2}):(\d{2})', time_str)
    if not match: return None
    hour = int(match.group(1))
    minute = int(match.group(2))
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now: target += datetime.timedelta(days=1)
    return (target - now).total_seconds()

def format_time(seconds):
    if seconds < 60: return f"{int(seconds)} сек"
    elif seconds < 3600: return f"{int(seconds // 60)} мин"
    elif seconds < 86400: return f"{int(seconds // 3600)} ч"
    else: return f"{int(seconds // 86400)} дн"

print("🤖 Бот запущен!")
bot.infinity_polling()
