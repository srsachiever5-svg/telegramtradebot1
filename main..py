import os
import telebot
from flask import Flask
from openai import OpenAI
from threading import Thread

# 1. Setup Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# 2. Initialize OpenAI Client (Hugging Face Router)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# 3. Initialize Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

# 4. Initialize Flask App (Required for Render)
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running live!", 200

# 5. Telegram Message Handler
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Show "typing..." action in Telegram
        bot.send_chat_action(message.chat.id, 'typing')

        # Call Hugging Face API with DeepSeek model
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V4-Pro:novita",
            messages=[
                {"role": "user", "content": message.text}
            ],
            stream=False
        )

        # Get response content
        response_text = chat_completion.choices[0].message.content
        
        # Send back to Telegram
        bot.reply_to(message, response_text)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Sorry, I encountered an error processing that request.")

# 6. Function to run the bot
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Start the bot in a separate thread
    Thread(target=run_bot).start()
    
    # Start Flask server on the port provided by Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
