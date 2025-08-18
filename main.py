import telebot
import os

API_KEY = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá 👋 Sou o Arqui Bot!")

bot.polling()
