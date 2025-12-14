import telebot

# Твой токен (я уже вставил тот, что ты прислал)
TOKEN = '8400022159:AAH5pQcA8hziNto4keJ4xMe9-TP6yAGx-0c'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой первый бот на Python 🐍\n"
                          "Я пока простой, но уже живой!\n\n"
                          "Напиши /help — покажу, что умею.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "🔹 /start — приветствие\n"
                          "🔹 /help — это меню\n"
                          "🔹 Напиши любое сообщение — я его повторю\n"
                          "🔹 Напиши математическое выражение (например 2+2*5) — посчитаю!")

# Эхо + простой калькулятор
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        # Пытаемся посчитать как математическое выражение
        result = eval(message.text)
        bot.reply_to(message, f"🔢 Результат: {result}")
    except:
        # Если не математика — просто повторяем
        bot.reply_to(message, f"💬 Ты написал: {message.text}")

print("🤖 Бот запущен и ждёт сообщений!")
bot.infinity_polling()
