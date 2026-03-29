import os
import telebot
import re
import pycountry
from dotenv import load_dotenv

from brain import agent_executor


load_dotenv()
BOT_TOKEN=os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    print("ERROR: Could not find TELEGRAM_BOT_TOKEN in .env file!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

def get_flag(country_name):
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.flag
    except:
        return "🌐"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = "✈️ <b>Welcome to Atlas Travel Agent!</b> \n\nTell me where you want to go. (e.g., 'Find me flights from Budapest to Barcelona on 2026-05-14')"
    bot.reply_to(message, welcome_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"\n--> Received from {message.from_user.first_name}: {message.text}")
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        # 1. Get the response from the AI
        response = agent_executor.invoke({"messages": [("user", message.text)]})
        final_text = response["messages"][-1].content
        
        country_matches = re.findall(r"\[([A-Za-z\s]+)\]", final_text)
        for country_name in country_matches:
            flag = get_flag(country_name)
            final_text = final_text.replace(f"[{country_name}]", f"{flag}")
        bot.send_message(
            message.chat.id,
            text=final_text,
            parse_mode="HTML" 
        )
        print("--> Replied with high-quality design AND flags!")
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] The bot crashed because: {e}")
        bot.send_message(
            message.chat.id, 
            "⚠️ <b>Oops!</b> Our travel servers are experiencing high demand (everyone wants a cheap flight today!). Please wait about 15 seconds and try again.",
            parse_mode="HTML"
        )

if __name__ == "__main__":
    print("🚀 Telegram Bot is online and listening! Open Telegram and say hi.")
    bot.infinity_polling()