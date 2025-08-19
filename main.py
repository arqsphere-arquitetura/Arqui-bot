import os
import telebot

API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(func=lambda message: True)
def reply(message):
    bot.reply_to(message, "Olá! O bot está ativo 🚀")

if __name__ == "__main__":
    print("Bot a correr...")
    bot.infinity_polling()
