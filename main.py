import osimport os
import telebot
from flask import Flask
from openai import OpenAI
from threading import Thread

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not set")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def health():
    return "Bot is running ✅", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')

        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V4-Pro:novita",
            messages=[{"role": "user", "content": message.text}],
        )

        text = response.choices[0].message.content or "No response"

        bot.reply_to(message, text)

    except Exception as e:
        print("ERROR:", e)
        bot.reply_to(message, "⚠️ Error occurred")

def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
