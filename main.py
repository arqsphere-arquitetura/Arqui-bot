import os
import telebot

# Lê a variável de ambiente API_KEY
API_KEY = os.getenv("API_KEY")

# Debug: mostra o valor carregado
print("API_KEY carregado:", API_KEY)

# Cria o bot com o token
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Olá! O bot está rodando no Render com sucesso 🚀")

print("Bot iniciado. Aguardando mensagens...")

bot.infinity_polling()
