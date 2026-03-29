import os
import telebot
import re
from dotenv import load_dotenv

from brain import agent_executor


load_dotenv()
BOT_TOKEN=os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    print("ERROR: Could not find TELEGRAM_BOT_TOKEN in .env file!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = "✈️ **Welcome to Atlas Travel Agent!** \n\nTell me where you want to go. (e.g., 'Find me flights from Budapest to Barcelona on 2026-05-14')"
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"\n--> Received from {message.from_user.first_name}: {message.text}")
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        # passing user message to model
        response = agent_executor.invoke({"messages": [("user", message.text)]})
        
        #text cleaning
        raw_content = response["messages"][-1].content
        if isinstance(raw_content, list):
            clean_text = raw_content[0]['text']
        else:
            clean_text = raw_content
        destination_match = re.search(r"to ([A-Za-z]+)", message.text)
        destination = destination_match.group(1) if destination_match else "travel"

        formatted_text = clean_text.replace(
            "- Direct Flights (0 stops)",
            "\n✈️ *Direct Flights (0 stops)*"
        ).replace(
            "- Transit Flights (1+ stops)",
            "\n🔁 *Transit Flights (1+ stops)*"
        )

        bot.send_message(
            message.chat.id,
            text=formatted_text,
            parse_mode="Markdown"
        )   
        print("--> Replied successfully!")
        
    except Exception as e:
        bot.reply_to(message, "Sorry, I am having trouble connecting to my systems. Please try again!")
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Telegram Bot is online and listening! Open Telegram and say hi.")
    bot.infinity_polling()