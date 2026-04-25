import requests
import telebot
import time
import threading
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # channel/group id

bot = telebot.TeleBot(BOT_TOKEN)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

# 🔹 Fetch data
def get_klines(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=50"
    data = requests.get(url).json()
    return [float(c[4]) for c in data]

# 🔹 MA
def ma(prices, n=14):
    return sum(prices[-n:]) / n

# 🔹 RSI
def rsi(prices, period=14):
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# 🔹 Signal logic (improved)
def signal(symbol):
    prices = get_klines(symbol)
    price = prices[-1]
    m = ma(prices)
    r = rsi(prices)

    if r < 30 and price > m:
        return "BUY 📈", price, r, m
    elif r > 70 and price < m:
        return "SELL 📉", price, r, m
    else:
        return "HOLD ⚖️", price, r, m

# 🔹 Command
@bot.message_handler(commands=['signal'])
def send_signal(msg):
    text = "📊 *Live Signals*\n\n"
    for s in SYMBOLS:
        sig, p, r, m = signal(s)
        text += f"{s}\nPrice: {p}\nRSI: {round(r,2)}\nMA: {round(m,2)}\n🔮 {sig}\n\n"

    bot.reply_to(msg, text, parse_mode="Markdown")

# 🔹 Auto send
def auto():
    while True:
        try:
            text = "🚀 *Auto Signals*\n\n"
            for s in SYMBOLS:
                sig, p, r, m = signal(s)
                text += f"{s}\n{sig}\nPrice: {p}\nRSI: {round(r,2)}\n\n"

            bot.send_message(CHAT_ID, text, parse_mode="Markdown")
        except Exception as e:
            print(e)

        time.sleep(300)

# 🔹 Run
threading.Thread(target=auto).start()
bot.infinity_polling()
