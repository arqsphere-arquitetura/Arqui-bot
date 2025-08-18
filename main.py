import os
import telebot

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY não encontrada. Define-a nas variáveis de ambiente do Fly.io.")

bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Olá 👋! Eu sou o Arqui-Bot. Pergunta qualquer coisa sobre os teus estudos.")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    user_text = message.text
    bot.reply_to(message, f"Recebi a tua pergunta: '{user_text}'. Em breve vou responder com base no conteúdo.")

print("🤖 Bot a correr...")
bot.infinity_polling()
