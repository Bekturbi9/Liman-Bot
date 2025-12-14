import telebot
import threading
import time
import datetime
import re

TOKEN = '8400022159:AAH5pQcA8hziNto4keJ4xMe9-TP6yAGx-0c'

bot = telebot.TeleBot(TOKEN)

# Список напоминаний: (chat_id, текст, время_в_секундах)
reminders = []

def schedule_reminders():
    while True:
        now = time.time()
        to_remove = []
        for i, (chat_id, text, remind_time) in enumerate(reminders):
            if now >= remind_time:
                bot.send_message(chat_id, f"🔔 Напоминание: {text}")
                to_remove.append(i)
        # Удаляем отправленные
        for i in reversed(to_remove):
            reminders.pop(i)
        time.sleep(1)  # Проверяем каждую секунду

# Запускаем фоновый поток для напоминаний
threading.Thread(target=schedule_reminders, daemon=True).start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой первый бот на Python 🐍\n"
                          "Я пока простой, но уже живой!\n\n"
                          "Напиши /help — покажу, что умею.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "🔹 /start — приветствие\n"
                          "🔹 /help — это меню\n"
                          "🔹 Напиши выражение (2+2*5) — посчитаю\n"
                          "🔹 Напиши «напомни [текст] через [время]» или «напомни [текст] в [время]»\n"
                          "   Примеры:\n"
                          "   • напомни купить хлеб через 30 минут\n"
                          "   • напомни позвонить другу в 18:00\n"
                          "   • напомни вынести мусор завтра в 20:00")

# Основной обработчик
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    text = message.text.lower().strip()

    # Сначала проверяем на напоминание
    if text.startswith('напомни '):
        parse_reminder(message)
        return

    # Потом математика
    try:
        result = eval(text)
        bot.reply_to(message, f"🔢 Результат: {result}")
        return
    except:
        pass

    # Если ничего — эхо
    bot.reply_to(message, f"💬 Ты написал: {text}")

def parse_reminder(message):
    text = message.text
    chat_id = message.chat.id

    # Ищем "через" или "в"
    if ' через ' in text:
        parts = text.split(' через ', 1)
        reminder_text = parts[0].replace('напомни ', '').strip()
        time_str = parts[1].strip()
        delay_seconds = parse_relative_time(time_str)
    elif ' в ' in text:
        parts = text.split(' в ', 1)
        reminder_text = parts[0].replace('напомни ', '').strip()
        time_str = parts[1].strip()
        delay_seconds = parse_absolute_time(time_str)
    else:
        bot.reply_to(message, "Не понял время. Используй «через ...» или «в ...»")
        return

    if delay_seconds is None:
        bot.reply_to(message, "Не смог разобрать время 😔\nПримеры: через 10 минут, в 18:30, завтра в 9:00")
        return

    remind_time = time.time() + delay_seconds
    reminders.append((chat_id, reminder_text, remind_time))

    bot.reply_to(message, f"✅ Ок! Напомню «{reminder_text}» через {format_time(delay_seconds)}")

def parse_relative_time(time_str):
    minutes = 0
    hours = 0
    days = 0

    if 'день' in time_str or 'дня' in time_str or 'дней' in time_str:
        match = re.search(r'(\d+)\s*(день|дня|дней)', time_str)
        if match:
            days = int(match.group(1))

    if 'час' in time_str:
        match = re.search(r'(\d+)\s*(час|часа|часов)', time_str)
        if match:
            hours = int(match.group(1))

    if 'минут' in time_str:
        match = re.search(r'(\d+)\s*(минут|минуты|минута)', time_str)
        if match:
            minutes = int(match.group(1))

    return days * 86400 + hours * 3600 + minutes * 60

def parse_absolute_time(time_str):
    now = datetime.datetime.now()
    target_time = None

    if 'завтра' in time_str:
        now += datetime.timedelta(days=1)
        time_str = time_str.replace('завтра', '').strip()

    match = re.search(r'(\d{1,2}):(\d{2})', time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_time < now:
            target_time += datetime.timedelta(days=1)

    if target_time:
        return (target_time - now).total_seconds()
    return None

def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)} секунд"
    elif seconds < 3600:
        return f"{int(seconds // 60)} минут"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} часов"
    else:
        return f"{int(seconds // 86400)} дней"

print("🤖 Бот запущен и ждёт сообщений!")
bot.infinity_polling()
